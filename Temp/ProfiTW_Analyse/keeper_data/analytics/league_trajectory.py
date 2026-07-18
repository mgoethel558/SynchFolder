"""Liga-Ebene Analytics (§7.1).

Aggregate über alle Torhüter eines Wettbewerbs:
* Verteilung des Debüt-Alters (erster Profieinsatz),
* typischer Pfad (Jugend → Leihe(n) → Profi),
* Einsatz-/Minuten-Progression nach Alter,
* Vereinsmobilität (Anzahl Klubs/Transfers),
* Karrierelängen.

Reine Funktion auf :class:`StoreFrames`; Ausgabe sind eigene Aggregate (NF-03).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ._loader import StoreFrames


def compute_league_trajectory(frames: StoreFrames, league_code: str) -> dict[str, Any]:
    """Berechnet die §7.1-Kennzahlen für eine Liga."""
    clubs = frames.clubs
    players = frames.players
    transfers = frames.transfers
    appearances = frames.appearances
    stations = frames.career_stations

    league_club_ids = set(
        clubs.loc[clubs["league"] == league_code, "club_id"].astype(str)
    )
    if not league_club_ids:
        return _empty_result(league_code)

    # GK-Spieler mit Bezug zur Liga (aktueller Klub oder Transfer/Station in Liga).
    player_ids = _league_player_ids(players, transfers, stations, league_club_ids)
    lp = players[players["player_id"].astype(str).isin(player_ids)].copy()

    return {
        "league": league_code,
        "goalkeeper_count": int(len(lp)),
        "debut_age_distribution": _debut_age_distribution(lp, appearances),
        "minutes_progression_by_age": _minutes_progression_by_age(lp, appearances),
        "club_mobility": _club_mobility(player_ids, transfers),
        "career_length": _career_length(player_ids, stations),
        "typical_path": _typical_path(player_ids, stations, frames.youth_clubs),
    }


def _league_player_ids(players, transfers, stations, league_club_ids) -> set[str]:
    ids: set[str] = set()
    ids |= set(
        players.loc[
            players["current_club_id"].astype(str).isin(league_club_ids), "player_id"
        ].astype(str)
    )
    for col in ("from_club_id", "to_club_id"):
        ids |= set(
            transfers.loc[
                transfers[col].astype(str).isin(league_club_ids), "player_id"
            ].astype(str)
        )
    ids |= set(
        stations.loc[
            stations["club_id"].astype(str).isin(league_club_ids), "player_id"
        ].astype(str)
    )
    # nur bekannte GK-Spieler
    gk = set(players["player_id"].astype(str))
    return ids & gk


def _debut_age_distribution(lp: pd.DataFrame, appearances: pd.DataFrame) -> dict:
    """Verteilung des Debüt-Alters über Appearance-Saisons.

    Ohne exaktes Spieldatum nähern wir das Debüt über die früheste Saison mit
    Minuten an und rechnen gegen das Geburtsjahr.
    """
    if lp.empty or appearances.empty:
        return {"histogram": {}, "count": 0}

    app = appearances.merge(
        lp[["player_id", "birth_date"]], on="player_id", how="inner"
    )
    app = app[app["minutes"].fillna(0) > 0]
    if app.empty:
        return {"histogram": {}, "count": 0}

    app["season_year"] = app["season"].apply(_season_start_year)
    debut = app.groupby("player_id")["season_year"].min().dropna()
    birth_year = (
        pd.to_datetime(lp.set_index("player_id")["birth_date"], errors="coerce")
        .dt.year
    )
    ages = (debut - birth_year).dropna()
    ages = ages[(ages > 12) & (ages < 45)]
    if ages.empty:
        return {"histogram": {}, "count": 0}

    hist = ages.round().astype(int).value_counts().sort_index()
    return {
        "histogram": {int(k): int(v) for k, v in hist.items()},
        "median_debut_age": float(ages.median()),
        "count": int(len(ages)),
    }


def _minutes_progression_by_age(lp: pd.DataFrame, appearances: pd.DataFrame) -> dict:
    if lp.empty or appearances.empty:
        return {}
    app = appearances.merge(
        lp[["player_id", "birth_date"]], on="player_id", how="inner"
    )
    app["season_year"] = app["season"].apply(_season_start_year)
    birth_year = pd.to_datetime(app["birth_date"], errors="coerce").dt.year
    app["age"] = app["season_year"] - birth_year
    app = app[(app["age"] > 12) & (app["age"] < 45)]
    if app.empty:
        return {}
    grouped = app.groupby(app["age"].round().astype(int))["minutes"].mean()
    return {int(k): round(float(v), 1) for k, v in grouped.dropna().items()}


def _club_mobility(player_ids: set[str], transfers: pd.DataFrame) -> dict:
    if transfers.empty:
        return {"avg_transfers": 0.0, "avg_distinct_clubs": 0.0}
    t = transfers[transfers["player_id"].astype(str).isin(player_ids)]
    if t.empty:
        return {"avg_transfers": 0.0, "avg_distinct_clubs": 0.0}
    per_player = t.groupby("player_id")
    avg_transfers = per_player.size().mean()
    distinct = per_player.apply(
        lambda g: pd.concat([g["from_club_id"], g["to_club_id"]]).nunique()
    ).mean()
    return {
        "avg_transfers": round(float(avg_transfers), 2),
        "avg_distinct_clubs": round(float(distinct), 2),
    }


def _career_length(player_ids: set[str], stations: pd.DataFrame) -> dict:
    if stations.empty:
        return {"avg_years": None, "count": 0}
    s = stations[stations["player_id"].astype(str).isin(player_ids)].copy()
    s["from_date"] = pd.to_datetime(s["from_date"], errors="coerce")
    s["to_date"] = pd.to_datetime(s["to_date"], errors="coerce")
    span = s.groupby("player_id").apply(
        lambda g: (g["to_date"].max() - g["from_date"].min()).days / 365.25
        if g["from_date"].notna().any() and g["to_date"].notna().any()
        else None
    ).dropna()
    if span.empty:
        return {"avg_years": None, "count": 0}
    return {"avg_years": round(float(span.mean()), 1), "count": int(len(span))}


def _typical_path(player_ids, stations, youth_clubs) -> dict:
    """Anteil GK mit Jugendverein und mit mind. einer Leih-Station."""
    n = len(player_ids) or 1
    with_youth = youth_clubs[
        youth_clubs["player_id"].astype(str).isin(player_ids)
    ]["player_id"].nunique()
    with_loan = stations[
        stations["player_id"].astype(str).isin(player_ids) & stations["is_loan"]
    ]["player_id"].nunique()
    return {
        "share_with_youth_club": round(with_youth / n, 3),
        "share_with_loan": round(with_loan / n, 3),
    }


def _season_start_year(season: Any) -> float:
    """'2019/20' oder '2019' -> 2019."""
    if season is None:
        return float("nan")
    s = str(season).strip()
    for sep in ("/", "-"):
        if sep in s:
            s = s.split(sep)[0]
            break
    digits = "".join(ch for ch in s if ch.isdigit())[:4]
    return float(digits) if len(digits) == 4 else float("nan")


def _empty_result(league_code: str) -> dict:
    return {
        "league": league_code,
        "goalkeeper_count": 0,
        "debut_age_distribution": {"histogram": {}, "count": 0},
        "minutes_progression_by_age": {},
        "club_mobility": {"avg_transfers": 0.0, "avg_distinct_clubs": 0.0},
        "career_length": {"avg_years": None, "count": 0},
        "typical_path": {"share_with_youth_club": 0.0, "share_with_loan": 0.0},
    }
