"""Export für die Homepage (F-09).

Schreibt statische JSON- (und CSV-)Dateien in das Export-Verzeichnis:

* ``feed.json``            – chronologischer Transfer-Feed (§7.3)
* ``league/<code>.json``   – Liga-Trajektorien (§7.1)
* ``club/<club_id>.json``  – Klub-Trajektorien (§7.2)
* ``meta.json``            – Lauf-Metadaten + Quellenattribution (NF-03/NF-08)

Es werden ausschließlich eigene Aggregationen exportiert — keine rohen
Fremd-Tabellen, keine Marktwerte (NF-03).
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .analytics._loader import StoreFrames
from .analytics.club_trajectory import compute_club_trajectory
from .analytics.feed import compute_transfer_feed
from .analytics.league_trajectory import compute_league_trajectory
from .config import Config
from .db import Database
from .logging_setup import get_logger

log = get_logger(__name__)


def run_export(config: Config, db: Database) -> dict[str, Any]:
    """Berechnet Analytics und schreibt die Export-Dateien. Gibt eine
    Zusammenfassung der geschriebenen Artefakte zurück."""
    frames = StoreFrames(db)
    export_dir = config.export_dir
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / "league").mkdir(exist_ok=True)
    (export_dir / "club").mkdir(exist_ok=True)

    written: dict[str, Any] = {"leagues": [], "clubs": [], "feed_items": 0}

    # --- Feed (§7.3) ---------------------------------------------------
    feed = compute_transfer_feed(frames, config.observed_league_codes)
    _write_json(export_dir / "feed.json", feed)
    _write_csv(export_dir / "feed.csv", feed)
    written["feed_items"] = len(feed)

    # --- Liga-Trajektorien (§7.1) --------------------------------------
    for comp in config.senior_competitions:
        result = compute_league_trajectory(frames, comp.code)
        _write_json(export_dir / "league" / f"{comp.code}.json", result)
        written["leagues"].append(comp.code)

    # --- Klub-Trajektorien (§7.2) --------------------------------------
    # Für alle Klubs der beobachteten Ligen, die GK-Stationen haben.
    club_ids = _relevant_club_ids(frames, config.observed_league_codes)
    for club_id in club_ids:
        result = compute_club_trajectory(frames, club_id)
        if result["goalkeeper_count"] == 0:
            continue
        _write_json(export_dir / "club" / f"{club_id}.json", result)
        written["clubs"].append(club_id)

    # --- Meta ----------------------------------------------------------
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "attribution": config.export_attribution,
        "observed_leagues": sorted(config.observed_league_codes),
        "counts": {
            "goalkeepers": int(len(frames.players)),
            "clubs": int(len(frames.clubs)),
            "transfer_events": int(len(frames.transfers)),
            "leagues_exported": len(written["leagues"]),
            "clubs_exported": len(written["clubs"]),
            "feed_items": written["feed_items"],
        },
        "note": "Nur eigene Aggregationen. Keine Marktwerte, keine rohen Fremd-Tabellen.",
    }
    _write_json(export_dir / "meta.json", meta)

    log.info(
        "export: %d Feed-Einträge, %d Ligen, %d Klubs -> %s",
        written["feed_items"],
        len(written["leagues"]),
        len(written["clubs"]),
        export_dir,
    )
    return written


def _relevant_club_ids(frames: StoreFrames, observed: set[str]) -> list[str]:
    clubs = frames.clubs
    ids = clubs.loc[clubs["league"].isin(observed), "club_id"].astype(str)
    return sorted(set(ids))


def _write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, default=str)


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
