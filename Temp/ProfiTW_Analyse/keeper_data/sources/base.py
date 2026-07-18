"""Abstrakte Adapter-Schnittstelle für Datenquellen (§8).

Ein Adapter kennt nur seine Quelle und liefert rohe Records. Er weiß nichts
über das Zielschema, die DB oder die Change-Detection — das entkoppelt Quellen
und macht sie austauschbar (quellen-agnostisch, §1).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..config import Config, SourceConfig

# Record-Typen, die ein Adapter emittieren kann. normalize() verarbeitet sie.
RECORD_PLAYER = "player"
RECORD_CLUB = "club"
RECORD_TRANSFER = "transfer"
RECORD_APPEARANCE = "appearance"
RECORD_YOUTH_CLUB = "youth_club"
RECORD_CAREER_STATION = "career_station"


@dataclass
class RawRecord:
    """Ein roher, quellennaher Datensatz.

    ``record_type`` ist einer der RECORD_*-Konstanten, ``payload`` ein Dict mit
    quellennahen Feldern. ``source`` identifiziert den Adapter (NF-08).
    """

    record_type: str
    payload: dict[str, Any]
    source: str
    extra: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(ABC):
    """Basisklasse aller Datenquellen-Adapter."""

    #: eindeutiger Name, muss zum Schlüssel in config.sources passen
    name: str = "base"

    def __init__(self, config: Config, source_config: SourceConfig) -> None:
        self.config = config
        self.source_config = source_config
        self.options = source_config.options

    @property
    def enabled(self) -> bool:
        return self.source_config.enabled

    @abstractmethod
    def fetch(self) -> list[RawRecord]:
        """Holt die Rohdaten der Quelle. Darf Exceptions werfen; der
        Orchestrator (run.py) fängt sie ab (graceful degradation, NF-06)."""
        raise NotImplementedError
