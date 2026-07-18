"""SQLAlchemy-ORM-Modelle (Zielschema §6).

DB-agnostisch (SQLite im MVP, Postgres später via SQLAlchemy). Historisierung
über die append-only ``transfer_events`` plus Gültigkeitszeiträume in
``career_stations`` (bitemporal, F-07). Jeder Datensatz trägt ``source`` und
``ingested_at`` zur Nachvollziehbarkeit (NF-08).
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    player_id: Mapped[str] = mapped_column(String, primary_key=True)  # TM-ID
    name: Mapped[str | None] = mapped_column(String)
    birth_date: Mapped[date | None] = mapped_column(Date)
    nationality: Mapped[str | None] = mapped_column(String)
    position: Mapped[str | None] = mapped_column(String)  # gefiltert: "Goalkeeper"
    sub_position: Mapped[str | None] = mapped_column(String)
    current_club_id: Mapped[str | None] = mapped_column(ForeignKey("clubs.club_id"))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)

    current_club: Mapped["Club | None"] = relationship(foreign_keys=[current_club_id])
    youth_clubs: Mapped[list["PlayerYouthClub"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    career_stations: Mapped[list["CareerStation"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )


class Club(Base):
    __tablename__ = "clubs"

    club_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(String)
    league: Mapped[str | None] = mapped_column(String)  # L1, L2, GB1, U19-BL, ...
    country: Mapped[str | None] = mapped_column(String)
    is_youth: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)


class PlayerYouthClub(Base):
    """Jugendvereine eines Spielers (n pro Spieler)."""

    __tablename__ = "player_youth_clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.player_id"))
    youth_club_name: Mapped[str] = mapped_column(String)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)

    player: Mapped["Player"] = relationship(back_populates="youth_clubs")


class CareerStation(Base):
    """Stationen/Verweildauern eines Spielers (Gültigkeitszeitraum)."""

    __tablename__ = "career_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.player_id"))
    club_id: Mapped[str | None] = mapped_column(ForeignKey("clubs.club_id"))
    from_date: Mapped[date | None] = mapped_column(Date)
    to_date: Mapped[date | None] = mapped_column(Date)
    is_loan: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)

    player: Mapped["Player"] = relationship(back_populates="career_stations")


class TransferEvent(Base):
    """APPEND-ONLY Kern der Change-Detection (F-06).

    ``transfer_id`` ist die TM-Transfer-ID, falls vorhanden, sonst der
    kanonische Hash-Key aus normalize.transfer_key().
    """

    __tablename__ = "transfer_events"

    transfer_id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.player_id"))
    from_club_id: Mapped[str | None] = mapped_column(ForeignKey("clubs.club_id"))
    to_club_id: Mapped[str | None] = mapped_column(ForeignKey("clubs.club_id"))
    transfer_date: Mapped[date | None] = mapped_column(Date)
    season: Mapped[str | None] = mapped_column(String)
    window: Mapped[str | None] = mapped_column(String)  # "summer" | "winter"
    type: Mapped[str | None] = mapped_column(String)  # permanent|loan|free|loan_end|retired
    fee_eur: Mapped[float | None] = mapped_column(Float)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_loan: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)


class Appearance(Base):
    """Einsätze/Minuten für Entwicklungs-Analytics (soweit verfügbar)."""

    __tablename__ = "appearances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str] = mapped_column(ForeignKey("players.player_id"))
    club_id: Mapped[str | None] = mapped_column(ForeignKey("clubs.club_id"))
    competition: Mapped[str | None] = mapped_column(String)
    season: Mapped[str | None] = mapped_column(String)
    matches: Mapped[int | None] = mapped_column(Integer)
    minutes: Mapped[int | None] = mapped_column(Integer)
    goals_conceded: Mapped[int | None] = mapped_column(Integer)
    clean_sheets: Mapped[int | None] = mapped_column(Integer)

    source: Mapped[str | None] = mapped_column(String)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)


class IngestionRun(Base):
    """Lauf-Metadaten / Auditing."""

    __tablename__ = "ingestion_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    source: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)  # running|success|failed
    rows_new: Mapped[int] = mapped_column(Integer, default=0)
    rows_changed: Mapped[int] = mapped_column(Integer, default=0)
    detail: Mapped[str | None] = mapped_column(Text)  # z.B. Fehlermeldung


# Für die Appearance-Idempotenz brauchen wir einen fachlichen Schlüssel;
# er wird in change_detection über (player_id, club_id, competition, season)
# gebildet und beim Upsert verglichen.
