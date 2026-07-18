"""Strukturiertes Logging (NF-06).

Einfaches, abhängigkeitsarmes Setup auf Basis der stdlib. Optional
zeilenweises JSON, sonst menschenlesbares Format. Wird einmalig aus
``run.py`` konfiguriert; alle Module holen ihren Logger via ``get_logger``.
"""

from __future__ import annotations

import json
import logging
import sys


class _JsonFormatter(logging.Formatter):
    """Serialisiert LogRecords als eine JSON-Zeile."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Zusätzliche Felder (via logger.info(..., extra={"key": ...}))
        for key, value in record.__dict__.items():
            if key not in _STD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


# Standard-Attribute eines LogRecords, die wir im JSON-Modus nicht doppeln.
_STD_ATTRS = set(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
) | {"message", "asctime"}

_CONFIGURED = False


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Konfiguriert das Root-Logging genau einmal."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
