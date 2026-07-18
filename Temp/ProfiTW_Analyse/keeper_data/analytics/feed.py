"""Homepage-Feed (§7.3).

Chronologischer Torwart-Transfer-Feed der beobachteten Wettbewerbe, täglich
aktualisiert. Reine Funktion auf :class:`StoreFrames`; nur eigene Aggregate,
keine Marktwerte (NF-03).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ._loader import StoreFrames


def compute_transfer_feed(
    frames: StoreFrames, observed_leagues: set[str], limit: int = 200
) -> list[dict[str, Any]]:
    transfers = frames.transfers
    if transfers.empty:
        return []

    clubs = frames.clubs.set_index(frames.clubs["club_id"].astype(str))
    players = frames.players.set_index(frames.players["player_id"].astype(str))

    def club_league(cid) -> str | None:
        cid = str(cid)
        return clubs["league"].get(cid) if cid in clubs.index else None

    def club_name(cid) -> str | None:
        cid = str(cid)
        return clubs["name"].get(cid) if cid in clubs.index else None

    def player_name(pid) -> str | None:
        pid = str(pid)
        return players["name"].get(pid) if pid in players.index else None

    t = transfers.copy()
    t["from_league"] = t["from_club_id"].map(club_league)
    t["to_league"] = t["to_club_id"].map(club_league)

    # Nur Transfers mit Bezug zu einem beobachteten Wettbewerb.
    mask = t["from_league"].isin(observed_leagues) | t["to_league"].isin(observed_leagues)
    t = t[mask].copy()
    if t.empty:
        return []

    t["transfer_date"] = pd.to_datetime(t["transfer_date"], errors="coerce")
    t = t.sort_values("transfer_date", ascending=False, na_position="last").head(limit)

    feed: list[dict] = []
    for _, row in t.iterrows():
        tdate = row["transfer_date"]
        feed.append(
            {
                "transfer_id": row["transfer_id"],
                "player_id": row["player_id"],
                "player_name": player_name(row["player_id"]),
                "from_club": club_name(row["from_club_id"]),
                "to_club": club_name(row["to_club_id"]),
                "from_league": row["from_league"],
                "to_league": row["to_league"],
                "transfer_date": tdate.date().isoformat() if pd.notna(tdate) else None,
                "season": row["season"],
                "window": row["window"],
                "type": row["type"],
                "is_loan": bool(row["is_loan"]),
                "is_free": bool(row["is_free"]),
            }
        )
    return feed
