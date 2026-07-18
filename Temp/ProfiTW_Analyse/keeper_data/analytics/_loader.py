"""Gemeinsames Laden der Store-Tabellen in pandas DataFrames.

Zentralisiert die DB-Reads, damit die Analytics-Module rein auf DataFrames
arbeiten und leicht gegen Fixture-Stores testbar bleiben (NF-07).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from ..db import Database


class StoreFrames:
    """Lazy-geladene DataFrames der relevanten Tabellen."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self.players = self._read("players")
        self.clubs = self._read("clubs")
        self.transfers = self._read("transfer_events")
        self.appearances = self._read("appearances")
        self.career_stations = self._read("career_stations")
        self.youth_clubs = self._read("player_youth_clubs")

    def _read(self, table: str) -> pd.DataFrame:
        return pd.read_sql_table(table, self._db.engine)


def age_years(birth: pd.Series, ref: pd.Series | date) -> pd.Series:
    """Alter in Jahren zwischen Geburtsdatum und Referenzdatum (vektorisiert)."""
    birth = pd.to_datetime(birth, errors="coerce")
    ref = pd.to_datetime(ref, errors="coerce")
    delta = (ref - birth).dt.days / 365.25
    return delta.round(1)
