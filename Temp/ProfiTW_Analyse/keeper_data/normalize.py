"""Normalisierung: Roh-Records -> kanonisches Schema, GK-Filter (F-04).

Wandelt quellennahe :class:`RawRecord`-Payloads in typisierte, kanonische
Dicts um, die change_detection direkt persistieren kann. Enthält außerdem den
kanonischen Transfer-Key für Idempotenz (F-06) und den GK-Filter (F-04).
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from typing import Any

from .logging_setup import get_logger
from .sources.base import (
    RECORD_APPEARANCE,
    RECORD_CAREER_STATION,
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RECORD_YOUTH_CLUB,
    RawRecord,
)

log = get_logger(__name__)

# Werte, die als Torwart-Position gelten (quellenübergreifend).
GOALKEEPER_TOKENS = {"goalkeeper", "keeper", "tw", "torwart", "gk"}

# Transfer-Fenster-Normalisierung.
_WINDOW_SUMMER = "summer"
_WINDOW_WINTER = "winter"


def is_goalkeeper(position: str | None, sub_position: str | None = None) -> bool:
    """GK-Filter (F-04): tolerant gegenüber Schreibweisen/Sprachen."""
    for value in (position, sub_position):
        if value and value.strip().lower() in GOALKEEPER_TOKENS:
            return True
    return False


def transfer_key(
    player_id: str,
    from_club_id: str | None,
    to_club_id: str | None,
    season: str | None,
    window: str | None,
) -> str:
    """Kanonischer Transfer-Key (§6) für Idempotenz, wenn keine TM-ID vorliegt.

    ``hash(player_id, from_club_id, to_club_id, season, window)``.
    """
    raw = "|".join(
        str(x) if x is not None else ""
        for x in (player_id, from_club_id, to_club_id, season, window)
    )
    return "k" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def appearance_key(
    player_id: str,
    club_id: str | None,
    competition: str | None,
    season: str | None,
) -> str:
    """Fachlicher Schlüssel für Appearance-Idempotenz."""
    raw = "|".join(
        str(x) if x is not None else ""
        for x in (player_id, club_id, competition, season)
    )
    return "a" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def youth_club_key(player_id: str, youth_club_name: str) -> str:
    raw = f"{player_id}|{youth_club_name.strip().lower()}"
    return "y" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def career_station_key(
    player_id: str, club_id: str | None, from_date: date | None
) -> str:
    raw = f"{player_id}|{club_id or ''}|{from_date.isoformat() if from_date else ''}"
    return "c" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


# ---------------------------------------------------------------------------
# Parsing-Helfer (tolerant gegenüber fehlenden/rohen Werten)
# ---------------------------------------------------------------------------
def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _to_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%b %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "loan", "j", "ja"}


def normalize_window(value: Any, transfer_date: date | None = None) -> str | None:
    """Normalisiert das Transferfenster auf 'summer'/'winter'."""
    s = _to_str(value)
    if s:
        low = s.lower()
        if low.startswith(("s", "sommer")) or "summer" in low:
            return _WINDOW_SUMMER
        if low.startswith(("w", "winter")):
            return _WINDOW_WINTER
    # Fallback über den Monat: Winterfenster ~ Dez–Feb.
    if transfer_date:
        return _WINDOW_WINTER if transfer_date.month in (1, 2, 12) else _WINDOW_SUMMER
    return None


def classify_transfer_type(payload: dict[str, Any]) -> str:
    """Leitet den Transfer-Typ ab (permanent|loan|free|loan_end|retired)."""
    explicit = _to_str(payload.get("type"))
    if explicit:
        low = explicit.lower()
        for token in ("loan_end", "loan", "free", "retired", "permanent"):
            if token.replace("_", " ") in low or token in low:
                return token
    if _to_bool(payload.get("is_loan")) or _to_bool(payload.get("loan")):
        return "loan"
    fee = _to_float(payload.get("fee_eur") or payload.get("fee"))
    if _to_bool(payload.get("is_free")) or (fee is not None and fee == 0):
        return "free"
    return "permanent"


# ---------------------------------------------------------------------------
# Kanonische Datensätze
# ---------------------------------------------------------------------------
def normalize_records(
    records: list[RawRecord],
    observed_leagues: set[str] | None = None,
    now: datetime | None = None,
) -> dict[str, list[dict]]:
    """Normalisiert Roh-Records nach kanonischem Schema und wendet den
    GK-Filter an.

    Rückgabe: Dict record_type -> Liste kanonischer Dicts. Spieler, die keine
    Torhüter sind, werden verworfen; alle abhängigen Records nur behalten, wenn
    ihr Spieler als GK bekannt ist.
    """
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)

    players: dict[str, dict] = {}
    clubs: dict[str, dict] = {}
    transfers: list[dict] = []
    appearances: list[dict] = []
    youth_clubs: list[dict] = []
    career_stations: list[dict] = []

    # 1) Zuerst Spieler sammeln, um GK-Zugehörigkeit zu kennen.
    gk_players: set[str] = set()
    for rec in records:
        if rec.record_type != RECORD_PLAYER:
            continue
        p = rec.payload
        pid = _to_str(p.get("player_id"))
        if not pid:
            continue
        position = _to_str(p.get("position"))
        sub_position = _to_str(p.get("sub_position"))
        if not is_goalkeeper(position, sub_position):
            continue  # F-04: nur Torhüter
        gk_players.add(pid)
        players[pid] = {
            "player_id": pid,
            "name": _to_str(p.get("name")),
            "birth_date": _to_date(p.get("birth_date") or p.get("date_of_birth")),
            "nationality": _to_str(p.get("nationality") or p.get("country_of_birth")),
            "position": "Goalkeeper",
            "sub_position": sub_position,
            "current_club_id": _to_str(p.get("current_club_id")),
            "last_seen_at": now,
            "source": rec.source,
            "ingested_at": now,
        }

    # 2) Clubs (unabhängig vom GK-Filter, aber optional auf Ligen begrenzt).
    for rec in records:
        if rec.record_type != RECORD_CLUB:
            continue
        c = rec.payload
        cid = _to_str(c.get("club_id"))
        if not cid:
            continue
        league = _to_str(c.get("league"))
        clubs[cid] = {
            "club_id": cid,
            "name": _to_str(c.get("name")),
            "league": league,
            "country": _to_str(c.get("country")),
            "is_youth": _to_bool(c.get("is_youth")),
            "source": rec.source,
            "ingested_at": now,
        }

    # 3) Abhängige Records nur für bekannte GK-Spieler.
    for rec in records:
        p = rec.payload
        pid = _to_str(p.get("player_id"))
        if rec.record_type == RECORD_TRANSFER:
            if not pid or pid not in gk_players:
                continue
            transfers.append(_normalize_transfer(rec, now))
        elif rec.record_type == RECORD_APPEARANCE:
            if not pid or pid not in gk_players:
                continue
            appearances.append(_normalize_appearance(rec, now))
        elif rec.record_type == RECORD_YOUTH_CLUB:
            if not pid or pid not in gk_players:
                continue
            name = _to_str(p.get("youth_club_name"))
            if name:
                youth_clubs.append(
                    {
                        "key": youth_club_key(pid, name),
                        "player_id": pid,
                        "youth_club_name": name,
                        "source": rec.source,
                        "ingested_at": now,
                    }
                )
        elif rec.record_type == RECORD_CAREER_STATION:
            if not pid or pid not in gk_players:
                continue
            from_date = _to_date(p.get("from_date"))
            cid = _to_str(p.get("club_id"))
            career_stations.append(
                {
                    "key": career_station_key(pid, cid, from_date),
                    "player_id": pid,
                    "club_id": cid,
                    "from_date": from_date,
                    "to_date": _to_date(p.get("to_date")),
                    "is_loan": _to_bool(p.get("is_loan")),
                    "source": rec.source,
                    "ingested_at": now,
                }
            )

    log.info(
        "normalize: %d GK-Spieler, %d Clubs, %d Transfers, %d Appearances, "
        "%d Jugendvereine, %d Stationen",
        len(players),
        len(clubs),
        len(transfers),
        len(appearances),
        len(youth_clubs),
        len(career_stations),
    )

    return {
        RECORD_PLAYER: list(players.values()),
        RECORD_CLUB: list(clubs.values()),
        RECORD_TRANSFER: transfers,
        RECORD_APPEARANCE: appearances,
        RECORD_YOUTH_CLUB: youth_clubs,
        RECORD_CAREER_STATION: career_stations,
    }


def _normalize_transfer(rec: RawRecord, now: datetime) -> dict:
    p = rec.payload
    pid = _to_str(p.get("player_id"))
    from_club = _to_str(p.get("from_club_id"))
    to_club = _to_str(p.get("to_club_id"))
    season = _to_str(p.get("season"))
    tdate = _to_date(p.get("transfer_date") or p.get("date"))
    window = normalize_window(p.get("window") or p.get("transfer_season"), tdate)
    ttype = classify_transfer_type(p)

    # NF-03: Marktwerte werden NICHT übernommen. Nur die tatsächliche Ablöse
    # (fee) als reines Transfer-Faktum, falls die Quelle sie liefert.
    fee = _to_float(p.get("fee_eur") or p.get("fee") or p.get("transfer_fee"))

    tm_id = _to_str(p.get("transfer_id"))
    key = tm_id or transfer_key(pid, from_club, to_club, season, window)

    return {
        "transfer_id": key,
        "player_id": pid,
        "from_club_id": from_club,
        "to_club_id": to_club,
        "transfer_date": tdate,
        "season": season,
        "window": window,
        "type": ttype,
        "fee_eur": fee,
        "is_free": ttype == "free",
        "is_loan": ttype in ("loan", "loan_end"),
        "source": rec.source,
        "ingested_at": now,
    }


def _normalize_appearance(rec: RawRecord, now: datetime) -> dict:
    p = rec.payload
    pid = _to_str(p.get("player_id"))
    cid = _to_str(p.get("club_id"))
    competition = _to_str(p.get("competition") or p.get("competition_id"))
    season = _to_str(p.get("season"))
    return {
        "key": appearance_key(pid, cid, competition, season),
        "player_id": pid,
        "club_id": cid,
        "competition": competition,
        "season": season,
        "matches": _to_int(p.get("matches") or p.get("games")),
        "minutes": _to_int(p.get("minutes") or p.get("minutes_played")),
        "goals_conceded": _to_int(p.get("goals_conceded")),
        "clean_sheets": _to_int(p.get("clean_sheets")),
        "source": rec.source,
        "ingested_at": now,
    }
