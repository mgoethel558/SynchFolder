"""Zentrale Konfiguration (NF-05).

Lädt ``config.yaml`` und überlagert sie mit Werten aus ``.env`` /
Umgebungsvariablen. Gibt eine gefrorene Dataclass-Struktur zurück, damit die
restliche Pipeline typisiert und ohne globale Streuung auf die Config zugreift.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Projektwurzel = Verzeichnis oberhalb des Pakets.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


@dataclass(frozen=True)
class Competition:
    code: str
    name: str
    country: str
    tier: str
    competition_id: str | None = None


@dataclass(frozen=True)
class SourceConfig:
    name: str
    enabled: bool
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HttpConfig:
    user_agent: str
    min_delay_seconds: float
    timeout_seconds: float
    max_retries: int
    backoff_base_seconds: float
    respect_robots_txt: bool


@dataclass(frozen=True)
class Config:
    database_url: str
    export_dir: Path
    export_attribution: str
    competitions: list[Competition]
    sources: dict[str, SourceConfig]
    http: HttpConfig
    log_level: str
    log_json: bool
    project_root: Path

    # -- Komfort-Zugriffe ---------------------------------------------------
    def source(self, name: str) -> SourceConfig | None:
        return self.sources.get(name)

    @property
    def senior_competitions(self) -> list[Competition]:
        return [c for c in self.competitions if c.tier == "senior"]

    @property
    def youth_competitions(self) -> list[Competition]:
        return [c for c in self.competitions if c.tier == "youth"]

    @property
    def observed_league_codes(self) -> set[str]:
        return {c.code for c in self.competitions}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(config_path: Path | str | None = None) -> Config:
    """Lädt und materialisiert die Konfiguration.

    Reihenfolge: config.yaml -> .env / Umgebungsvariablen (überschreiben).
    """
    load_dotenv(PROJECT_ROOT / ".env")

    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    raw = _load_yaml(path)

    # --- Datenbank ---------------------------------------------------------
    db_url = os.getenv("DATABASE_URL") or raw.get("database", {}).get(
        "url", "sqlite:///keeper_data.db"
    )

    # --- Export ------------------------------------------------------------
    export_raw = raw.get("export", {})
    export_dir = PROJECT_ROOT / export_raw.get("dir", "export")

    # --- Wettbewerbe -------------------------------------------------------
    comps_raw = raw.get("competitions", {})
    competitions: list[Competition] = []
    for tier_key in ("senior", "youth"):
        for entry in comps_raw.get(tier_key, []):
            competitions.append(
                Competition(
                    code=entry["code"],
                    name=entry.get("name", entry["code"]),
                    country=entry.get("country", ""),
                    tier=entry.get("tier", tier_key),
                    competition_id=entry.get("competition_id"),
                )
            )

    # --- Quellen -----------------------------------------------------------
    sources: dict[str, SourceConfig] = {}
    for name, opts in (raw.get("sources", {}) or {}).items():
        opts = opts or {}
        enabled = bool(opts.pop("enabled", False))
        sources[name] = SourceConfig(name=name, enabled=enabled, options=opts)

    # --- HTTP --------------------------------------------------------------
    http_raw = raw.get("http", {})
    http = HttpConfig(
        user_agent=http_raw.get("user_agent", "KeeperPartnerBot/0.1"),
        min_delay_seconds=float(http_raw.get("min_delay_seconds", 2.0)),
        timeout_seconds=float(http_raw.get("timeout_seconds", 20.0)),
        max_retries=int(http_raw.get("max_retries", 3)),
        backoff_base_seconds=float(http_raw.get("backoff_base_seconds", 1.0)),
        respect_robots_txt=bool(http_raw.get("respect_robots_txt", True)),
    )

    # --- Logging -----------------------------------------------------------
    log_raw = raw.get("logging", {})

    return Config(
        database_url=db_url,
        export_dir=export_dir,
        export_attribution=export_raw.get("attribution", ""),
        competitions=competitions,
        sources=sources,
        http=http,
        log_level=os.getenv("LOG_LEVEL") or log_raw.get("level", "INFO"),
        log_json=bool(log_raw.get("json", False)),
        project_root=PROJECT_ROOT,
    )
