"""Tests für Normalisierung: GK-Filter, Transfer-Key, Feld-Mapping (F-04, F-06)."""

from __future__ import annotations

from keeper_data.normalize import (
    classify_transfer_type,
    is_goalkeeper,
    normalize_records,
    normalize_window,
    transfer_key,
)
from keeper_data.sources.base import (
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RECORD_YOUTH_CLUB,
    RawRecord,
)


def test_is_goalkeeper_tolerant():
    assert is_goalkeeper("Goalkeeper")
    assert is_goalkeeper("Torwart")
    assert is_goalkeeper(None, "GK")
    assert not is_goalkeeper("Attack")
    assert not is_goalkeeper(None, None)


def test_transfer_key_stable_and_unique():
    k1 = transfer_key("1", "27", "39", "23/24", "summer")
    k2 = transfer_key("1", "27", "39", "23/24", "summer")
    k3 = transfer_key("1", "27", "39", "22/23", "summer")
    assert k1 == k2  # deterministisch -> Idempotenz
    assert k1 != k3


def test_normalize_window_fallback_by_month():
    from datetime import date

    assert normalize_window("Sommer") == "summer"
    assert normalize_window("W") == "winter"
    assert normalize_window(None, date(2024, 1, 15)) == "winter"
    assert normalize_window(None, date(2024, 7, 1)) == "summer"


def test_classify_transfer_type():
    assert classify_transfer_type({"is_loan": True}) == "loan"
    assert classify_transfer_type({"fee_eur": 0, "is_free": True}) == "free"
    assert classify_transfer_type({"fee_eur": 5_000_000}) == "permanent"
    assert classify_transfer_type({"type": "loan_end"}) == "loan_end"


def test_normalize_filters_non_goalkeepers():
    records = [
        RawRecord(RECORD_PLAYER, {"player_id": "1", "position": "Goalkeeper"}, "test"),
        RawRecord(RECORD_PLAYER, {"player_id": "2", "position": "Attack"}, "test"),
        # Transfer eines Feldspielers -> muss verworfen werden
        RawRecord(RECORD_TRANSFER, {"player_id": "2", "from_club_id": "10",
                                    "to_club_id": "20", "season": "23/24"}, "test"),
        # Transfer des Torwarts -> bleibt
        RawRecord(RECORD_TRANSFER, {"player_id": "1", "from_club_id": "10",
                                    "to_club_id": "20", "season": "23/24"}, "test"),
        RawRecord(RECORD_YOUTH_CLUB, {"player_id": "1",
                                      "youth_club_name": "TSV Musterstadt"}, "test"),
    ]
    out = normalize_records(records)
    assert len(out[RECORD_PLAYER]) == 1
    assert out[RECORD_PLAYER][0]["player_id"] == "1"
    assert len(out[RECORD_TRANSFER]) == 1
    assert out[RECORD_TRANSFER][0]["player_id"] == "1"
    assert len(out[RECORD_YOUTH_CLUB]) == 1


def test_normalize_does_not_carry_market_value():
    # NF-03: es darf kein market_value-Feld in den kanonischen Transfer geraten.
    rec = RawRecord(
        RECORD_TRANSFER,
        {"player_id": "1", "from_club_id": "1", "to_club_id": "2",
         "season": "23/24", "market_value": 9_000_000, "fee_eur": 1_000_000},
        "test",
    )
    player = RawRecord(RECORD_PLAYER, {"player_id": "1", "position": "Goalkeeper"}, "test")
    out = normalize_records([player, rec])
    t = out[RECORD_TRANSFER][0]
    assert "market_value" not in t
    assert t["fee_eur"] == 1_000_000
