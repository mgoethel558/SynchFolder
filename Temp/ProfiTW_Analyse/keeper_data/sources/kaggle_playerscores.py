"""Kaggle-Adapter: Basis-Historie aus ``davidcariboo/player-scores`` (F-01).

Der Datensatz ist relational (players, clubs, transfers, appearances,
competitions). Wir laden ihn mit ``kagglehub`` + pandas, wenn ein Kaggle-Token
vorhanden ist — andernfalls fällt der Adapter auf lokale CSVs im konfigurierten
Verzeichnis zurück (``data/kaggle/``), sodass der Bootstrap auch ohne Token
testbar ist.

Es werden früh nur die beobachteten Wettbewerbe (§2.1) behalten und der
GK-Filter greift später zentral in ``normalize``. Marktwerte werden bewusst
nicht emittiert (NF-03) — nur Transfer-Fakten (inkl. Ablöse).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Config, SourceConfig
from ..logging_setup import get_logger
from .base import (
    RECORD_APPEARANCE,
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RawRecord,
    SourceAdapter,
)

log = get_logger(__name__)

# CSV-Dateien im Datensatz (Kaggle-Namen). Bei fehlenden Dateien wird
# graceful übersprungen.
_FILES = {
    "players": "players.csv",
    "clubs": "clubs.csv",
    "transfers": "transfers.csv",
    "appearances": "appearances.csv",
    "competitions": "competitions.csv",
}


class KagglePlayerScoresAdapter(SourceAdapter):
    name = "kaggle_playerscores"

    def fetch(self) -> list[RawRecord]:
        data_dir = self._resolve_data_dir()
        if data_dir is None:
            log.warning(
                "kaggle: weder Kaggle-Download noch lokaler CSV-Ordner verfügbar — "
                "Quelle liefert 0 Records."
            )
            return []

        frames = self._load_frames(data_dir)
        records: list[RawRecord] = []
        observed = self.config.observed_league_codes

        # --- Clubs -------------------------------------------------------
        club_league: dict[str, str] = {}
        clubs_df = frames.get("clubs")
        comps_df = frames.get("competitions")
        comp_code_by_id = self._competition_code_map(comps_df)

        if clubs_df is not None:
            for _, row in clubs_df.iterrows():
                cid = _s(row.get("club_id"))
                if not cid:
                    continue
                comp_id = _s(row.get("domestic_competition_id"))
                league = comp_code_by_id.get(comp_id, comp_id)
                club_league[cid] = league or ""
                records.append(
                    RawRecord(
                        record_type=RECORD_CLUB,
                        source=self.name,
                        payload={
                            "club_id": cid,
                            "name": _s(row.get("name")) or _s(row.get("club_name")),
                            "league": league,
                            "country": _s(row.get("country")),
                            "is_youth": False,
                        },
                    )
                )

        # --- Players (nur GK werden später behalten) ---------------------
        players_df = frames.get("players")
        gk_player_ids: set[str] = set()
        if players_df is not None:
            for _, row in players_df.iterrows():
                pid = _s(row.get("player_id"))
                if not pid:
                    continue
                position = _s(row.get("position"))
                sub_position = _s(row.get("sub_position"))
                if position and position.lower() != "goalkeeper" and (
                    not sub_position or "goalkeeper" not in sub_position.lower()
                ):
                    continue  # frühes Aussortieren spart Speicher
                gk_player_ids.add(pid)
                records.append(
                    RawRecord(
                        record_type=RECORD_PLAYER,
                        source=self.name,
                        payload={
                            "player_id": pid,
                            "name": _s(row.get("name")),
                            "birth_date": _s(row.get("date_of_birth")),
                            "nationality": _s(row.get("country_of_citizenship"))
                            or _s(row.get("country_of_birth")),
                            "position": position,
                            "sub_position": sub_position,
                            "current_club_id": _s(row.get("current_club_id")),
                        },
                    )
                )

        # --- Transfers (nur für GK, nur beobachtete Ligen) ---------------
        transfers_df = frames.get("transfers")
        if transfers_df is not None:
            for _, row in transfers_df.iterrows():
                pid = _s(row.get("player_id"))
                if not pid or pid not in gk_player_ids:
                    continue
                from_club = _s(row.get("from_club_id"))
                to_club = _s(row.get("to_club_id"))
                if observed and not (
                    club_league.get(from_club, "") in observed
                    or club_league.get(to_club, "") in observed
                ):
                    continue
                records.append(
                    RawRecord(
                        record_type=RECORD_TRANSFER,
                        source=self.name,
                        payload={
                            "transfer_id": _s(row.get("transfer_id")),
                            "player_id": pid,
                            "from_club_id": from_club,
                            "to_club_id": to_club,
                            "transfer_date": _s(row.get("transfer_date")),
                            "season": _s(row.get("transfer_season")),
                            "window": None,
                            # NF-03: KEIN market_value; nur echte Ablöse.
                            "fee_eur": row.get("transfer_fee"),
                        },
                    )
                )

        # --- Appearances (nur für GK) ------------------------------------
        app_df = frames.get("appearances")
        if app_df is not None:
            records.extend(self._appearance_records(app_df, gk_player_ids))

        log.info("kaggle: %d Roh-Records erzeugt (%d GK-Spieler)",
                 len(records), len(gk_player_ids))
        return records

    # ------------------------------------------------------------------
    def _appearance_records(
        self, app_df: pd.DataFrame, gk_ids: set[str]
    ) -> list[RawRecord]:
        """Aggregiert die Appearance-Zeilen (pro Spiel) je Saison/Club/Wettbewerb."""
        df = app_df.copy()
        df["player_id"] = df["player_id"].map(_s)
        df = df[df["player_id"].isin(gk_ids)]
        if df.empty:
            return []

        # Erwartete Spalten robust behandeln.
        for col in ("minutes_played", "goals_conceded", "clean_sheets"):
            if col not in df.columns:
                df[col] = 0
        group_cols = [c for c in ("player_id", "player_club_id", "competition_id")
                      if c in df.columns]
        season_col = "season" if "season" in df.columns else None
        if season_col:
            group_cols.append(season_col)

        agg = (
            df.groupby(group_cols, dropna=False)
            .agg(
                matches=("game_id", "count") if "game_id" in df.columns
                else ("player_id", "count"),
                minutes=("minutes_played", "sum"),
                goals_conceded=("goals_conceded", "sum"),
                clean_sheets=("clean_sheets", "sum"),
            )
            .reset_index()
        )

        records: list[RawRecord] = []
        for _, row in agg.iterrows():
            records.append(
                RawRecord(
                    record_type=RECORD_APPEARANCE,
                    source=self.name,
                    payload={
                        "player_id": _s(row.get("player_id")),
                        "club_id": _s(row.get("player_club_id")),
                        "competition": _s(row.get("competition_id")),
                        "season": _s(row.get(season_col)) if season_col else None,
                        "matches": row.get("matches"),
                        "minutes": row.get("minutes"),
                        "goals_conceded": row.get("goals_conceded"),
                        "clean_sheets": row.get("clean_sheets"),
                    },
                )
            )
        return records

    # ------------------------------------------------------------------
    def _competition_code_map(self, comps_df: pd.DataFrame | None) -> dict[str, str]:
        """competition_id -> interner Liga-Code (falls beobachtet)."""
        mapping: dict[str, str] = {}
        if comps_df is None:
            return mapping
        observed_ids = {
            c.competition_id: c.code
            for c in self.config.competitions
            if c.competition_id
        }
        for _, row in comps_df.iterrows():
            comp_id = _s(row.get("competition_id"))
            if comp_id in observed_ids:
                mapping[comp_id] = observed_ids[comp_id]
            elif comp_id:
                mapping[comp_id] = comp_id
        return mapping

    def _resolve_data_dir(self) -> Path | None:
        """Bestimmt das Datenverzeichnis: erst Kaggle-Download, dann lokaler
        CSV-Fallback."""
        # 1) Kaggle-Download versuchen (nur wenn Token vorhanden).
        import os

        if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
            try:
                import kagglehub

                path = kagglehub.dataset_download(
                    self.options.get("dataset", "davidcariboo/player-scores")
                )
                log.info("kaggle: Datensatz via kagglehub geladen: %s", path)
                return Path(path)
            except Exception as exc:  # noqa: BLE001 - graceful degradation
                log.warning("kaggle: Download fehlgeschlagen (%s), nutze CSV-Fallback", exc)

        # 2) Lokaler CSV-Fallback.
        local = self.options.get("local_csv_dir")
        if local:
            local_path = (self.config.project_root / local).resolve()
            if local_path.exists():
                log.info("kaggle: nutze lokale CSVs aus %s", local_path)
                return local_path
        return None

    def _load_frames(self, data_dir: Path) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        for key, filename in _FILES.items():
            fpath = data_dir / filename
            if fpath.exists():
                try:
                    frames[key] = pd.read_csv(fpath, low_memory=False)
                except Exception as exc:  # noqa: BLE001
                    log.warning("kaggle: %s konnte nicht gelesen werden: %s", filename, exc)
        return frames


def _s(value) -> str | None:
    """pandas-toleranter String-Cast (NaN -> None)."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return None
    # Ints kommen aus pandas oft als "123.0" -> normalisieren für IDs.
    if s.endswith(".0") and s[:-2].isdigit():
        return s[:-2]
    return s
