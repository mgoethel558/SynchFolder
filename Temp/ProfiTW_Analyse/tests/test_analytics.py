"""Tests für Analytics (§7.1/§7.2) und End-to-End-Pipeline (F-08/F-09/DoD).

Nutzt den Kaggle-CSV-Fallback (Demo-Daten) als Quelle und läuft die Pipeline
gegen eine temporäre SQLite-DB — deckt Bootstrap, Idempotenz, Analytics und
Export in einem Rutsch ab.
"""

from __future__ import annotations

import json

import pytest

from keeper_data.analytics._loader import StoreFrames
from keeper_data.analytics.club_trajectory import compute_club_trajectory
from keeper_data.analytics.feed import compute_transfer_feed
from keeper_data.analytics.league_trajectory import compute_league_trajectory
from keeper_data.change_detection import apply_changes
from keeper_data.config import load_config
from keeper_data.db import Database
from keeper_data.normalize import normalize_records
from keeper_data.sources.kaggle_playerscores import KagglePlayerScoresAdapter


@pytest.fixture
def populated_db():
    config = load_config()
    db = Database("sqlite:///:memory:")
    db.init_db()
    adapter = KagglePlayerScoresAdapter(config, config.source("kaggle_playerscores"))
    normalized = normalize_records(
        adapter.fetch(), observed_leagues=config.observed_league_codes
    )
    with db.session() as s:
        apply_changes(s, normalized)
    return config, db


def test_league_trajectory_bundesliga(populated_db):
    config, db = populated_db
    frames = StoreFrames(db)
    result = compute_league_trajectory(frames, "L1")
    assert result["league"] == "L1"
    assert result["goalkeeper_count"] >= 1
    # Debüt-Alter-Verteilung wurde aus Appearances berechnet.
    assert "histogram" in result["debut_age_distribution"]


def test_club_trajectory_bayern(populated_db):
    config, db = populated_db
    frames = StoreFrames(db)
    result = compute_club_trajectory(frames, "27")  # Bayern München
    assert result["club_id"] == "27"
    # Nübel (4) wechselte von Bayern weg -> als Torwart mit Bezug zum Klub.
    assert result["goalkeeper_count"] >= 1
    assert "origin_breakdown" in result


def test_transfer_feed_only_observed_leagues(populated_db):
    config, db = populated_db
    frames = StoreFrames(db)
    feed = compute_transfer_feed(frames, config.observed_league_codes)
    assert isinstance(feed, list)
    for item in feed:
        assert item["from_league"] in config.observed_league_codes or \
            item["to_league"] in config.observed_league_codes


def test_end_to_end_export(tmp_path):
    """DoD: python-Pipeline erzeugt Export-Dateien; zweiter Lauf ist idempotent."""
    from dataclasses import replace

    from keeper_data.export import run_export

    config = load_config()
    config = replace(config, export_dir=tmp_path / "export")
    db = Database("sqlite:///:memory:")
    db.init_db()

    adapter = KagglePlayerScoresAdapter(config, config.source("kaggle_playerscores"))

    # Erster Lauf.
    with db.session() as s:
        stats1 = apply_changes(
            s, normalize_records(adapter.fetch(),
                                 observed_leagues=config.observed_league_codes)
        )
    # Zweiter Lauf -> keine neuen Transfers (Idempotenz).
    with db.session() as s:
        stats2 = apply_changes(
            s, normalize_records(adapter.fetch(),
                                 observed_leagues=config.observed_league_codes)
        )
    assert stats1.new_transfers > 0
    assert stats2.new_transfers == 0

    run_export(config, db)

    feed_file = config.export_dir / "feed.json"
    meta_file = config.export_dir / "meta.json"
    l1_file = config.export_dir / "league" / "L1.json"
    assert feed_file.exists() and meta_file.exists() and l1_file.exists()

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    assert meta["counts"]["goalkeepers"] >= 1
    # NF-03: kein Marktwert im veröffentlichten Feed.
    feed = json.loads(feed_file.read_text(encoding="utf-8"))
    for item in feed:
        assert "market_value" not in item
