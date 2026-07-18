"""Klub-Ebene Analytics (§7.2).

Gefiltert auf einen Klub:
* Torwart-Pfad-Muster am Verein über die Zeit (chronologische Stationen),
* Herkunft je Torwart (eigene Jugend / geliehen / gekauft),
* Verweildauer je Torwart.

Reine Funktion auf :class:`StoreFrames`; nur eigene Aggregate (NF-03).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ._loader import StoreFrames


def compute_club_trajectory(frames: StoreFrames, club_id: str) -> dict[str, Any]:
    club_id = str(club_id)
    clubs = frames.clubs
    stations = frames.career_stations
    transfers = frames.transfers
    youth = frames.youth_clubs
    players = frames.players

    club_row = clubs[clubs["club_id"].astype(str) == club_id]
    club_name = club_row["name"].iloc[0] if not club_row.empty else None

    gk_ids = set(players["player_id"].astype(str))

    club_stations = stations[stations["club_id"].astype(str) == club_id].copy()
    gk_at_club: set[str] = set(club_stations["player_id"].astype(str))
    # Ergänzung/Fallback: alle GK mit Transfer-Bezug zum Klub (Zu- ODER Abgang).
    if not transfers.empty:
        related = transfers[
            (transfers["to_club_id"].astype(str) == club_id)
            | (transfers["from_club_id"].astype(str) == club_id)
        ]
        gk_at_club |= set(related["player_id"].astype(str))
    gk_at_club &= gk_ids

    keepers = []
    for pid in sorted(gk_at_club):
        keepers.append(
            _keeper_summary(pid, club_id, club_stations, transfers, youth, players)
        )

    # Nach Startdatum sortieren -> Nachfolge-/Pfad-Muster über die Zeit.
    keepers.sort(key=lambda k: (k["from_date"] or "9999"))

    return {
        "club_id": club_id,
        "club_name": club_name,
        "goalkeeper_count": len(keepers),
        "keepers": keepers,
        "origin_breakdown": _origin_breakdown(keepers),
    }


def _keeper_summary(pid, club_id, club_stations, transfers, youth, players) -> dict:
    name_row = players[players["player_id"].astype(str) == pid]
    name = name_row["name"].iloc[0] if not name_row.empty else None

    from_date = to_date = None
    is_loan = False
    if not club_stations.empty:
        st = club_stations[club_stations["player_id"].astype(str) == pid]
        if not st.empty:
            fd = pd.to_datetime(st["from_date"], errors="coerce")
            td = pd.to_datetime(st["to_date"], errors="coerce")
            from_date = fd.min().date().isoformat() if fd.notna().any() else None
            to_date = td.max().date().isoformat() if td.notna().any() else None
            is_loan = bool(st["is_loan"].any())

    tenure_years = None
    if from_date and to_date:
        tenure_years = round(
            (pd.to_datetime(to_date) - pd.to_datetime(from_date)).days / 365.25, 1
        )

    return {
        "player_id": pid,
        "name": name,
        "from_date": from_date,
        "to_date": to_date,
        "tenure_years": tenure_years,
        "origin": _classify_origin(pid, club_id, transfers, youth, is_loan),
    }


def _classify_origin(pid, club_id, transfers, youth, is_loan) -> str:
    """eigene Jugend | Leihe | Transfer (gekauft/verpflichtet) | unbekannt."""
    if is_loan:
        return "loan"
    # eigener Jugendverein? (Name-Match schwierig; Näherung: Jugendverein vorhanden
    # und kein eingehender Transfer zum Klub)
    incoming = transfers[
        (transfers["player_id"].astype(str) == pid)
        & (transfers["to_club_id"].astype(str) == club_id)
    ]
    if incoming.empty:
        has_youth = not youth[youth["player_id"].astype(str) == pid].empty
        return "own_youth" if has_youth else "unknown"
    row = incoming.iloc[0]
    if bool(row.get("is_loan")):
        return "loan"
    if bool(row.get("is_free")):
        return "free_transfer"
    return "transfer"


def _origin_breakdown(keepers: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for k in keepers:
        counts[k["origin"]] = counts.get(k["origin"], 0) + 1
    return counts
