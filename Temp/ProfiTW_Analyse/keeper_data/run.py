"""Batch-Einstiegspunkt der Pipeline (F-10).

Aufruf:
    python -m keeper_data.run [--config config.yaml] [--only kaggle_playerscores]
                              [--skip-analytics] [--skip-export]

Ablauf (§8/§10):
1. Config laden, DB init/migrate.
2. Je aktiver Quelle: fetch() -> normalize() -> change_detection().
   Fehler einer Quelle brechen den Gesamtlauf nicht ab (NF-06).
3. ingestion_runs protokollieren.
4. Analytics neu berechnen + Export für die Homepage.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from .change_detection import ChangeStats, apply_changes
from .config import Config, load_config
from .db import Database
from .export import run_export
from .logging_setup import configure_logging, get_logger
from .models import IngestionRun
from .normalize import normalize_records
from .sources.base import SourceAdapter
from .sources.kaggle_playerscores import KagglePlayerScoresAdapter
from .sources.tm_delta_scraper import TransfermarktDeltaAdapter
from .sources.tm_youth_scraper import TransfermarktYouthAdapter

log = get_logger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Registry: Adapter-Name -> Klasse. Neue Quellen hier eintragen (§8).
ADAPTER_REGISTRY: dict[str, type[SourceAdapter]] = {
    KagglePlayerScoresAdapter.name: KagglePlayerScoresAdapter,
    TransfermarktDeltaAdapter.name: TransfermarktDeltaAdapter,
    TransfermarktYouthAdapter.name: TransfermarktYouthAdapter,
}


def build_adapters(config: Config, only: set[str] | None) -> list[SourceAdapter]:
    adapters: list[SourceAdapter] = []
    for name, cls in ADAPTER_REGISTRY.items():
        src_cfg = config.source(name)
        if src_cfg is None:
            continue
        if only and name not in only:
            continue
        if not src_cfg.enabled and not (only and name in only):
            log.info("Quelle '%s' ist deaktiviert — übersprungen.", name)
            continue
        adapters.append(cls(config, src_cfg))
    return adapters


def run_source(db: Database, adapter: SourceAdapter, observed: set[str]) -> ChangeStats:
    """Führt eine Quelle aus und persistiert idempotent. Protokolliert einen
    ingestion_run. Wirft NICHT — Fehler werden gefangen und als 'failed'
    protokolliert (NF-06)."""
    stats = ChangeStats()
    with db.session() as session:
        run = IngestionRun(
            started_at=_utcnow(), source=adapter.name, status="running"
        )
        session.add(run)
        session.flush()
        run_id = run.run_id

    try:
        raw = adapter.fetch()
        normalized = normalize_records(raw, observed_leagues=observed)
        with db.session() as session:
            stats = apply_changes(session, normalized)
        status, detail = "success", None
    except Exception as exc:  # noqa: BLE001 - graceful degradation
        log.exception("Quelle '%s' fehlgeschlagen: %s", adapter.name, exc)
        status, detail = "failed", str(exc)

    with db.session() as session:
        run = session.get(IngestionRun, run_id)
        run.finished_at = _utcnow()
        run.status = status
        run.rows_new = stats.rows_new
        run.rows_changed = stats.rows_changed
        run.detail = detail
    return stats


def run(
    config_path: str | None = None,
    only: set[str] | None = None,
    skip_analytics: bool = False,
    skip_export: bool = False,
) -> int:
    config = load_config(config_path)
    configure_logging(config.log_level, config.log_json)
    log.info("KeeperPartner Pipeline gestartet.")

    db = Database(config.database_url)
    db.init_db()

    adapters = build_adapters(config, only)
    if not adapters:
        log.warning("Keine aktiven Quellen. Nur Analytics/Export laufen.")

    observed = config.observed_league_codes
    total = ChangeStats()
    for adapter in adapters:
        log.info("--- Quelle: %s ---", adapter.name)
        total.merge(run_source(db, adapter, observed))

    log.info(
        "Ingestion abgeschlossen: %d neue Transfers, %d geändert.",
        total.new_transfers,
        total.changed_transfers,
    )

    # Analytics werden im Zuge des Exports berechnet (§8, Schritt 5+6).
    if skip_export:
        log.info("Export/Analytics übersprungen (--skip-export).")
    else:
        run_export(config, db)

    log.info("Pipeline erfolgreich beendet.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KeeperPartner Torwart-Daten-Pipeline")
    parser.add_argument("--config", default=None, help="Pfad zu config.yaml")
    parser.add_argument(
        "--only",
        action="append",
        help="Nur diese Quelle(n) ausführen (mehrfach nutzbar).",
    )
    parser.add_argument("--skip-analytics", action="store_true")
    parser.add_argument("--skip-export", action="store_true")
    args = parser.parse_args(argv)

    only = set(args.only) if args.only else None
    return run(
        config_path=args.config,
        only=only,
        skip_analytics=args.skip_analytics,
        skip_export=args.skip_export,
    )


if __name__ == "__main__":
    sys.exit(main())
