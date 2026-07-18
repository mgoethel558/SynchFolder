"""Transfermarkt-Delta-Scraper: tagesfrische Transfers (F-02).

Steuert die Transfer-Übersichtsseiten der beobachteten Senior-Wettbewerbe
(§2.1) an und extrahiert Transfer-*Fakten*. **Keine Marktwerte** (NF-03).

Die Netzwerk- und Parse-Ebene sind getrennt: :meth:`fetch` holt HTML über den
höflichen Client (NF-02), :func:`parse_transfers_page` ist eine reine Funktion
und wird gegen HTML-Fixtures getestet (NF-07). Die HTML-Struktur von TM kann
sich ändern — Selektoren sind hier zentral gehalten und leicht anpassbar.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..config import Config, SourceConfig
from ..http_client import PoliteClient
from ..logging_setup import get_logger
from .base import RECORD_CLUB, RECORD_PLAYER, RECORD_TRANSFER, RawRecord, SourceAdapter

log = get_logger(__name__)

# TM-Spieler-/Club-IDs stecken in den Profil-URLs: /name/profil/spieler/<id>
_PLAYER_ID_RE = re.compile(r"/spieler/(\d+)")
_CLUB_ID_RE = re.compile(r"/verein/(\d+)")


class TransfermarktDeltaAdapter(SourceAdapter):
    name = "tm_delta_scraper"

    def fetch(self) -> list[RawRecord]:
        base_url = self.options.get("base_url", "https://www.transfermarkt.de")
        season = self.options.get("season", 2024)
        path_tpl = self.options.get(
            "transfers_path",
            "/wettbewerb/transfers/wettbewerb/{competition_id}/saison_id/{season}",
        )

        records: list[RawRecord] = []
        with PoliteClient(self.config.http) as client:
            for comp in self.config.senior_competitions:
                if not comp.competition_id:
                    continue
                url = base_url + path_tpl.format(
                    competition_id=comp.competition_id,
                    comp_slug=comp.code.lower(),
                    season=season,
                )
                try:
                    html = client.get(url)
                except Exception as exc:  # noqa: BLE001
                    log.warning("tm_delta: %s fehlgeschlagen: %s", url, exc)
                    continue
                if not html:
                    continue
                page_records = parse_transfers_page(
                    html, source=self.name, league=comp.code, season=str(season)
                )
                log.info("tm_delta: %s -> %d Records", comp.code, len(page_records))
                records.extend(page_records)
        return records


def parse_transfers_page(
    html: str, source: str, league: str | None = None, season: str | None = None
) -> list[RawRecord]:
    """Reine Parse-Funktion: extrahiert Transfer-Records aus TM-HTML.

    Erwartet die klassische Transfer-Grid-Struktur (Boxen je Verein mit je zwei
    Tabellen für Zu-/Abgänge). Tolerant gegenüber fehlenden Feldern — was nicht
    gefunden wird, bleibt ``None``.
    """
    soup = BeautifulSoup(html, "html.parser")
    records: list[RawRecord] = []
    seen_players: set[str] = set()
    seen_clubs: set[str] = set()

    for box in soup.select("div.box"):
        # Vereins-Kontext der Box (der Klub, dessen Zu-/Abgänge gelistet sind).
        box_club_id, box_club_name = _extract_box_club(box)
        if box_club_id and box_club_id not in seen_clubs:
            seen_clubs.add(box_club_id)
            records.append(
                RawRecord(
                    record_type=RECORD_CLUB,
                    source=source,
                    payload={
                        "club_id": box_club_id,
                        "name": box_club_name,
                        "league": league,
                    },
                )
            )

        for table in box.select("table.items"):
            is_departure = _is_departure_table(box, table)
            for row in table.select("tbody > tr"):
                rec = _parse_transfer_row(
                    row, box_club_id, is_departure, source, league, season
                )
                if rec is None:
                    continue
                player_rec, transfer_rec = rec
                pid = player_rec.payload["player_id"]
                if pid not in seen_players:
                    seen_players.add(pid)
                    records.append(player_rec)
                records.append(transfer_rec)

    return records


def _extract_box_club(box) -> tuple[str | None, str | None]:
    link = box.select_one("a[href*='/verein/']")
    if not link:
        return None, None
    m = _CLUB_ID_RE.search(link.get("href", ""))
    club_id = m.group(1) if m else None
    name = link.get_text(strip=True) or None
    return club_id, name


def _is_departure_table(box, table) -> bool:
    """Heuristik: TM überschreibt Zu-/Abgänge; 'Abgänge'/'out' => departure."""
    header = ""
    prev = table.find_previous(["h2", "div"], class_=re.compile("table-header|content-box-headline"))
    if prev:
        header = prev.get_text(" ", strip=True).lower()
    return "abgang" in header or "abgänge" in header or "departure" in header or "out" in header


def _parse_transfer_row(
    row, box_club_id, is_departure, source, league, season
):
    player_link = row.select_one("a[href*='/spieler/']")
    if not player_link:
        return None
    m = _PLAYER_ID_RE.search(player_link.get("href", ""))
    if not m:
        return None
    player_id = m.group(1)
    player_name = player_link.get_text(strip=True) or None

    # Gegenverein der Zeile (woher/wohin).
    other_club_id = None
    for a in row.select("a[href*='/verein/']"):
        cm = _CLUB_ID_RE.search(a.get("href", ""))
        if cm:
            other_club_id = cm.group(1)
            break

    # Zu-/Abgang bestimmt Richtung.
    if is_departure:
        from_club_id, to_club_id = box_club_id, other_club_id
    else:
        from_club_id, to_club_id = other_club_id, box_club_id

    # Position (für GK-Filter) — TM nennt sie meist in einer Unterzeile.
    position = None
    pos_cell = row.select_one(".pos, td.zentriert + td .inline-table tr:nth-of-type(2)")
    if pos_cell:
        position = pos_cell.get_text(strip=True) or None

    fee_text = _row_fee_text(row)

    player_rec = RawRecord(
        record_type=RECORD_PLAYER,
        source=source,
        payload={
            "player_id": player_id,
            "name": player_name,
            "position": position,
            "current_club_id": to_club_id,
        },
    )
    transfer_rec = RawRecord(
        record_type=RECORD_TRANSFER,
        source=source,
        payload={
            "player_id": player_id,
            "from_club_id": from_club_id,
            "to_club_id": to_club_id,
            "season": season,
            # NF-03: kein Marktwert; nur Ablöse-Faktum (falls interpretierbar).
            "fee_eur": _parse_fee_eur(fee_text),
            "is_free": bool(fee_text and _is_free_text(fee_text)),
            "is_loan": bool(fee_text and ("leih" in fee_text.lower() or "loan" in fee_text.lower())),
        },
    )
    return player_rec, transfer_rec


def _is_free_text(text: str) -> bool:
    """Erkennt ablösefreie Wechsel (dt./engl.)."""
    low = text.lower()
    return "free" in low or "ablösefrei" in low or "ablosefrei" in low


def _row_fee_text(row) -> str | None:
    cell = row.select_one("td.rechts, td.rechts.hauptlink")
    return cell.get_text(strip=True) if cell else None


def _parse_fee_eur(text: str | None) -> float | None:
    """Wandelt eine Ablöse-Angabe (z.B. '5,00 Mio. €') in EUR um.

    Marktwerte werden NICHT geparst (NF-03) — diese Funktion arbeitet nur auf
    dem Ablöse-Feld der Transferzeile.
    """
    if not text:
        return None
    low = text.lower().replace(",", ".")
    num_match = re.search(r"([\d.]+)", low)
    if not num_match:
        return None
    try:
        value = float(num_match.group(1))
    except ValueError:
        return None
    if "mio" in low or "m" in low.split():
        value *= 1_000_000
    elif "tsd" in low or "k" in low.split():
        value *= 1_000
    return value
