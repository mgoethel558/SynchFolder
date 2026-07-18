"""Datenbank-Layer: Engine, Schema-Init, generische Upserts.

Kapselt SQLAlchemy, sodass die Pipeline DB-agnostisch bleibt (SQLite -> Postgres).
Die Upserts sind bewusst einfach (SELECT-then-INSERT/UPDATE per PK) gehalten,
damit sie über Backends hinweg funktionieren und für den Batch-Durchsatz im
MVP genügen.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class Database:
    def __init__(self, url: str, echo: bool = False) -> None:
        self.url = url
        connect_args = {}
        if url.startswith("sqlite"):
            # SQLite: gleiche Session über Threads hinweg unkritisch im Batch.
            connect_args = {"check_same_thread": False}
        self.engine: Engine = create_engine(url, echo=echo, connect_args=connect_args)
        self._Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def init_db(self) -> None:
        """Erzeugt fehlende Tabellen (create_all ist idempotent)."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Transaktions-Kontext: commit bei Erfolg, rollback bei Fehler."""
        session = self._Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def upsert_by_pk(
    session: Session,
    model: type,
    pk_field: str,
    pk_value,
    values: dict,
) -> bool:
    """Fügt eine Zeile ein oder aktualisiert sie anhand des Primärschlüssels.

    Gibt ``True`` zurück, wenn eine neue Zeile eingefügt wurde, sonst ``False``
    (nur relevante Felder werden bei bestehenden Zeilen überschrieben — ``None``
    überschreibt nicht, um partielle Quellen nicht zu leeren).
    """
    obj = session.get(model, pk_value)
    if obj is None:
        session.add(model(**{pk_field: pk_value, **values}))
        return True

    for key, val in values.items():
        if val is not None:
            setattr(obj, key, val)
    return False
