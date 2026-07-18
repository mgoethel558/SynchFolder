"""Change-Detection & Persistenz (F-06, F-07, NF-04).

Nimmt normalisierte Datensätze und schreibt sie idempotent in den Store:

* ``transfer_events`` sind append-only und werden über ihren kanonischen Key
  dedupliziert — ein zweiter Lauf erzeugt keine Duplikate.
* Current-State-Tabellen (players, clubs, career_stations, youth_clubs,
  appearances) werden per Upsert aktualisiert.

Gibt eine Zählung (neu/geändert) je Record-Typ zurück, die run.py in
``ingestion_runs`` protokolliert.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import upsert_by_pk
from .logging_setup import get_logger
from .models import (
    Appearance,
    CareerStation,
    Club,
    Player,
    PlayerYouthClub,
    TransferEvent,
)
from .normalize import appearance_key, career_station_key, youth_club_key
from .sources.base import (
    RECORD_APPEARANCE,
    RECORD_CAREER_STATION,
    RECORD_CLUB,
    RECORD_PLAYER,
    RECORD_TRANSFER,
    RECORD_YOUTH_CLUB,
)

log = get_logger(__name__)


@dataclass
class ChangeStats:
    new_transfers: int = 0
    changed_transfers: int = 0
    rows_new: int = 0
    rows_changed: int = 0
    new_transfer_ids: list[str] = field(default_factory=list)

    def merge(self, other: "ChangeStats") -> None:
        self.new_transfers += other.new_transfers
        self.changed_transfers += other.changed_transfers
        self.rows_new += other.rows_new
        self.rows_changed += other.rows_changed
        self.new_transfer_ids.extend(other.new_transfer_ids)


def apply_changes(session: Session, normalized: dict[str, list[dict]]) -> ChangeStats:
    """Persistiert normalisierte Records idempotent. Ein bestehender
    Datensatz mit identischem Schlüssel wird aktualisiert (nicht dupliziert)."""
    stats = ChangeStats()

    # Reihenfolge beachtet FKs: Clubs & Player zuerst.
    _upsert_clubs(session, normalized.get(RECORD_CLUB, []), stats)
    _upsert_players(session, normalized.get(RECORD_PLAYER, []), stats)
    session.flush()

    _apply_transfers(session, normalized.get(RECORD_TRANSFER, []), stats)
    _upsert_career_stations(session, normalized.get(RECORD_CAREER_STATION, []), stats)
    _upsert_youth_clubs(session, normalized.get(RECORD_YOUTH_CLUB, []), stats)
    _upsert_appearances(session, normalized.get(RECORD_APPEARANCE, []), stats)

    log.info(
        "change_detection: %d neue Transfers, %d geänderte; rows_new=%d rows_changed=%d",
        stats.new_transfers,
        stats.changed_transfers,
        stats.rows_new,
        stats.rows_changed,
    )
    return stats


def _upsert_clubs(session: Session, rows: list[dict], stats: ChangeStats) -> None:
    for row in rows:
        inserted = upsert_by_pk(session, Club, "club_id", row["club_id"], row)
        stats.rows_new += int(inserted)
        stats.rows_changed += int(not inserted)


def _upsert_players(session: Session, rows: list[dict], stats: ChangeStats) -> None:
    for row in rows:
        inserted = upsert_by_pk(session, Player, "player_id", row["player_id"], row)
        stats.rows_new += int(inserted)
        stats.rows_changed += int(not inserted)


def _apply_transfers(session: Session, rows: list[dict], stats: ChangeStats) -> None:
    """Append-only mit Dedup über transfer_id (F-06).

    Neuer Key -> INSERT + Event. Bestehender Key -> nur Update, falls sich ein
    fachliches Feld geändert hat (kein Duplikat, keine Scheinänderung)."""
    for row in rows:
        tid = row["transfer_id"]
        existing = session.get(TransferEvent, tid)
        if existing is None:
            session.add(TransferEvent(**row))
            stats.new_transfers += 1
            stats.rows_new += 1
            stats.new_transfer_ids.append(tid)
            continue

        # Idempotenz: nur echte Feldänderungen zählen als "changed".
        changed = False
        for key in ("transfer_date", "season", "window", "type", "fee_eur",
                    "is_free", "is_loan", "to_club_id", "from_club_id"):
            new_val = row.get(key)
            if new_val is not None and getattr(existing, key) != new_val:
                setattr(existing, key, new_val)
                changed = True
        if changed:
            existing.ingested_at = row.get("ingested_at")
            existing.source = row.get("source")
            stats.changed_transfers += 1
            stats.rows_changed += 1


def _upsert_career_stations(
    session: Session, rows: list[dict], stats: ChangeStats
) -> None:
    for row in rows:
        key = row.pop("key", None) or career_station_key(
            row["player_id"], row.get("club_id"), row.get("from_date")
        )
        existing = session.scalar(
            select(CareerStation).where(
                CareerStation.player_id == row["player_id"],
                CareerStation.club_id == row.get("club_id"),
                CareerStation.from_date == row.get("from_date"),
            )
        )
        if existing is None:
            session.add(CareerStation(**row))
            stats.rows_new += 1
        else:
            for k in ("to_date", "is_loan", "source", "ingested_at"):
                if row.get(k) is not None:
                    setattr(existing, k, row[k])
            stats.rows_changed += 1


def _upsert_youth_clubs(session: Session, rows: list[dict], stats: ChangeStats) -> None:
    for row in rows:
        row.pop("key", None)
        existing = session.scalar(
            select(PlayerYouthClub).where(
                PlayerYouthClub.player_id == row["player_id"],
                PlayerYouthClub.youth_club_name == row["youth_club_name"],
            )
        )
        if existing is None:
            session.add(PlayerYouthClub(**row))
            stats.rows_new += 1
        # sonst: nichts zu tun (idempotent), zählt nicht als Änderung


def _upsert_appearances(session: Session, rows: list[dict], stats: ChangeStats) -> None:
    for row in rows:
        row.pop("key", None)
        existing = session.scalar(
            select(Appearance).where(
                Appearance.player_id == row["player_id"],
                Appearance.club_id == row.get("club_id"),
                Appearance.competition == row.get("competition"),
                Appearance.season == row.get("season"),
            )
        )
        if existing is None:
            session.add(Appearance(**row))
            stats.rows_new += 1
        else:
            changed = False
            for k in ("matches", "minutes", "goals_conceded", "clean_sheets"):
                if row.get(k) is not None and getattr(existing, k) != row[k]:
                    setattr(existing, k, row[k])
                    changed = True
            if changed:
                existing.ingested_at = row.get("ingested_at")
                stats.rows_changed += 1
