"""Tests für Change-Detection & Idempotenz (F-06, NF-04)."""

from __future__ import annotations

import pytest

from keeper_data.change_detection import apply_changes
from keeper_data.db import Database
from keeper_data.models import TransferEvent
from keeper_data.normalize import normalize_records
from keeper_data.sources.base import (
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RawRecord,
)


@pytest.fixture
def db():
    database = Database("sqlite:///:memory:")
    database.init_db()
    return database


def _sample_records():
    return [
        RawRecord(RECORD_CLUB, {"club_id": "27", "name": "Bayern", "league": "L1"}, "t"),
        RawRecord(RECORD_CLUB, {"club_id": "39", "name": "VfB", "league": "L1"}, "t"),
        RawRecord(RECORD_PLAYER, {"player_id": "4", "name": "Nübel",
                                  "position": "Goalkeeper", "current_club_id": "39"}, "t"),
        RawRecord(RECORD_TRANSFER, {"player_id": "4", "from_club_id": "27",
                                    "to_club_id": "39", "season": "23/24",
                                    "window": "summer"}, "t"),
    ]


def test_idempotent_rerun_creates_no_duplicates(db):
    normalized = normalize_records(_sample_records())

    with db.session() as s:
        stats1 = apply_changes(s, normalized)
    assert stats1.new_transfers == 1

    # Zweiter, direkt folgender Lauf mit identischen Daten.
    normalized2 = normalize_records(_sample_records())
    with db.session() as s:
        stats2 = apply_changes(s, normalized2)
    assert stats2.new_transfers == 0
    assert stats2.changed_transfers == 0

    with db.session() as s:
        assert s.query(TransferEvent).count() == 1


def test_changed_fee_marks_transfer_changed(db):
    with db.session() as s:
        apply_changes(s, normalize_records(_sample_records()))

    # Gleicher Transfer-Key, aber jetzt mit Ablöse -> als geändert erkannt.
    recs = _sample_records()
    recs[-1].payload["fee_eur"] = 2_000_000
    with db.session() as s:
        stats = apply_changes(s, normalize_records(recs))

    assert stats.new_transfers == 0
    assert stats.changed_transfers == 1
    with db.session() as s:
        t = s.query(TransferEvent).one()
        assert t.fee_eur == 2_000_000


def test_new_transfer_is_appended(db):
    with db.session() as s:
        apply_changes(s, normalize_records(_sample_records()))

    recs = _sample_records()
    recs.append(
        RawRecord(RECORD_TRANSFER, {"player_id": "4", "from_club_id": "39",
                                    "to_club_id": "27", "season": "24/25",
                                    "window": "summer"}, "t")
    )
    with db.session() as s:
        stats = apply_changes(s, normalize_records(recs))

    assert stats.new_transfers == 1
    with db.session() as s:
        assert s.query(TransferEvent).count() == 2
