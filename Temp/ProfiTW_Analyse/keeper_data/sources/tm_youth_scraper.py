"""Transfermarkt-Nachwuchs-Scraper (F-03).

Nachwuchs-Wettbewerbe (U17/U19-Bundesliga, U17–U21-Nationalteams) sind von
keinem Datensatz/keiner API abgedeckt. Dieser Adapter crawlt Kader-/Detail-
seiten der Nachwuchs-Wettbewerbe und liefert mindestens Kaderzugehörigkeit
(Spieler + Club + Karrierestation) sowie — soweit vorhanden — Jugendvereine.

Einsatz-/Minutendaten sind im Nachwuchs erwartungsgemäß lückenhaft (§12);
fehlende Felder bleiben ``None``. Netzwerk und Parsing sind getrennt (NF-07).
Keine Marktwerte (NF-03).
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..http_client import PoliteClient
from ..logging_setup import get_logger
from .base import (
    RECORD_CAREER_STATION,
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_YOUTH_CLUB,
    RawRecord,
    SourceAdapter,
)

log = get_logger(__name__)

_PLAYER_ID_RE = re.compile(r"/spieler/(\d+)")
_CLUB_ID_RE = re.compile(r"/verein/(\d+)")


class TransfermarktYouthAdapter(SourceAdapter):
    name = "tm_youth_scraper"

    def fetch(self) -> list[RawRecord]:
        base_url = self.options.get("base_url", "https://www.transfermarkt.de")
        # Konfigurierbare Liste von Kaderseiten je Nachwuchs-Wettbewerb.
        # Erwartet unter options["squad_urls"]: Liste von {league, url}.
        squad_urls = self.options.get("squad_urls", [])
        if not squad_urls:
            log.info(
                "tm_youth: keine squad_urls konfiguriert — Nachwuchs-Crawl übersprungen."
            )
            return []

        records: list[RawRecord] = []
        with PoliteClient(self.config.http) as client:
            for entry in squad_urls:
                url = entry["url"] if entry["url"].startswith("http") else base_url + entry["url"]
                league = entry.get("league")
                try:
                    html = client.get(url)
                except Exception as exc:  # noqa: BLE001
                    log.warning("tm_youth: %s fehlgeschlagen: %s", url, exc)
                    continue
                if not html:
                    continue
                page = parse_squad_page(html, source=self.name, league=league)
                log.info("tm_youth: %s -> %d Records", league, len(page))
                records.extend(page)
        return records


def parse_squad_page(
    html: str, source: str, league: str | None = None, club_id: str | None = None
) -> list[RawRecord]:
    """Reine Parse-Funktion: extrahiert Kader (Spieler als GK-Kandidaten) aus
    einer TM-Kaderseite. Der GK-Filter greift zentral in normalize."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[RawRecord] = []

    # Club-Kontext der Seite.
    if club_id is None:
        club_link = soup.select_one("a[href*='/verein/']")
        if club_link:
            m = _CLUB_ID_RE.search(club_link.get("href", ""))
            club_id = m.group(1) if m else None

    if club_id:
        club_name = None
        title = soup.select_one("h1")
        if title:
            club_name = title.get_text(strip=True) or None
        records.append(
            RawRecord(
                record_type=RECORD_CLUB,
                source=source,
                payload={
                    "club_id": club_id,
                    "name": club_name,
                    "league": league,
                    "is_youth": True,
                },
            )
        )

    for row in soup.select("table.items tbody > tr"):
        player_link = row.select_one("a[href*='/spieler/']")
        if not player_link:
            continue
        m = _PLAYER_ID_RE.search(player_link.get("href", ""))
        if not m:
            continue
        player_id = m.group(1)
        name = player_link.get_text(strip=True) or None

        position = None
        pos_cell = row.select_one(".inline-table tr:nth-of-type(2) td, td.pos")
        if pos_cell:
            position = pos_cell.get_text(strip=True) or None

        birth_date = _cell_text(row, "td.zentriert")

        records.append(
            RawRecord(
                record_type=RECORD_PLAYER,
                source=source,
                payload={
                    "player_id": player_id,
                    "name": name,
                    "position": position,
                    "birth_date": birth_date,
                    "current_club_id": club_id,
                },
            )
        )
        # Kaderzugehörigkeit als (offene) Karrierestation.
        records.append(
            RawRecord(
                record_type=RECORD_CAREER_STATION,
                source=source,
                payload={
                    "player_id": player_id,
                    "club_id": club_id,
                    "from_date": None,
                    "to_date": None,
                    "is_loan": False,
                },
            )
        )

    return records


def parse_player_youth_clubs(
    html: str, player_id: str, source: str
) -> list[RawRecord]:
    """Extrahiert Jugendvereine aus einer TM-Spielerprofilseite (F-05).

    TM listet Jugendvereine als kommaseparierte Namen in einem Datenblock.
    """
    soup = BeautifulSoup(html, "html.parser")
    records: list[RawRecord] = []

    label = soup.find(string=re.compile(r"Jugendverein", re.I))
    if not label:
        return records
    container = label.find_parent()
    if not container:
        return records
    value_el = container.find_next_sibling() or container.find_next()
    if not value_el:
        return records
    text = value_el.get_text(" ", strip=True)
    for name in re.split(r",|/", text):
        name = name.strip()
        if name:
            records.append(
                RawRecord(
                    record_type=RECORD_YOUTH_CLUB,
                    source=source,
                    payload={"player_id": player_id, "youth_club_name": name},
                )
            )
    return records


def _cell_text(row, selector: str) -> str | None:
    cell = row.select_one(selector)
    return cell.get_text(strip=True) if cell else None
