"""Tests für Adapter: Kaggle-CSV-Fallback + TM-HTML-Parsing (NF-07)."""

from __future__ import annotations

from pathlib import Path

from keeper_data.config import load_config
from keeper_data.sources.base import (
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RECORD_YOUTH_CLUB,
)
from keeper_data.sources.kaggle_playerscores import KagglePlayerScoresAdapter
from keeper_data.sources.tm_delta_scraper import parse_transfers_page
from keeper_data.sources.tm_youth_scraper import parse_player_youth_clubs

FIXTURES = Path(__file__).parent / "fixtures"


def test_kaggle_csv_fallback_filters_goalkeepers():
    """Der Kaggle-Adapter liest die Demo-CSVs und emittiert nur GK-Spieler."""
    config = load_config()
    src = config.source("kaggle_playerscores")
    adapter = KagglePlayerScoresAdapter(config, src)
    records = adapter.fetch()

    player_ids = {
        r.payload["player_id"] for r in records if r.record_type == RECORD_PLAYER
    }
    # Feldspieler (100 Musiala, 101 Bellingham) dürfen NICHT auftauchen.
    assert "100" not in player_ids
    assert "101" not in player_ids
    assert {"1", "2", "3", "4", "5"} <= player_ids

    # Clubs werden auf interne Liga-Codes gemappt.
    clubs = {r.payload["club_id"]: r.payload for r in records if r.record_type == RECORD_CLUB}
    assert clubs["27"]["league"] == "L1"

    # Transfers eines Feldspielers wurden verworfen (nur GK-Transfers bleiben).
    transfer_players = {
        r.payload["player_id"] for r in records if r.record_type == RECORD_TRANSFER
    }
    assert "100" not in transfer_players


def test_kaggle_no_market_value_field():
    """NF-03: es wird kein Marktwert emittiert, nur die Ablöse (fee_eur)."""
    config = load_config()
    adapter = KagglePlayerScoresAdapter(config, config.source("kaggle_playerscores"))
    for rec in adapter.fetch():
        if rec.record_type == RECORD_TRANSFER:
            assert "market_value" not in rec.payload
            assert "fee_eur" in rec.payload


def test_parse_transfers_page_directions_and_positions():
    html = (FIXTURES / "tm_transfers_L1.html").read_text(encoding="utf-8")
    records = parse_transfers_page(html, source="tm_delta_scraper", league="L1",
                                   season="2024")

    transfers = [r for r in records if r.record_type == RECORD_TRANSFER]
    by_player = {t.payload["player_id"]: t.payload for t in transfers}

    # Zugang Neuer: von Schalke (33) zu Bayern (27).
    assert by_player["1"]["to_club_id"] == "27"
    assert by_player["1"]["from_club_id"] == "33"
    assert by_player["1"]["is_free"] is True

    # Abgang Nübel: von Bayern (27) zu Stuttgart (39), als Leihe.
    assert by_player["4"]["from_club_id"] == "27"
    assert by_player["4"]["to_club_id"] == "39"
    assert by_player["4"]["is_loan"] is True

    # Positionen wurden mitgelesen (für GK-Filter).
    players = {r.payload["player_id"]: r.payload for r in records
               if r.record_type == RECORD_PLAYER}
    assert players["1"]["position"] == "Torwart"


def test_parse_player_youth_clubs():
    html = """
    <html><body>
      <span class="info-table__content--regular">Jugendvereine</span>
      <span class="info-table__content--bold">FC Gelsenkirchen-Buer, FC Schalke 04</span>
    </body></html>
    """
    records = parse_player_youth_clubs(html, player_id="1", source="tm_youth")
    names = {r.payload["youth_club_name"] for r in records}
    assert records and all(r.record_type == RECORD_YOUTH_CLUB for r in records)
    assert "FC Schalke 04" in names
