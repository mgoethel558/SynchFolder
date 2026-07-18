# KeeperPartner – Torwart-Daten-Pipeline

Täglicher Python-Batch-Job, der torhüter-bezogene Fußballdaten (Transfers +
Karriere-/Jugendhistorie) einsammelt, historisiert, auswertet und statisch für
eine Homepage exportiert. Fokus: **nur Torhüter**, **Batch statt Echtzeit**,
Betrieb **~0 €/Monat** auf kostenlosen Tiers.

Siehe das vollständige Anforderungsdokument für Scope, Datenmodell und
Akzeptanzkriterien.

## Schnellstart

```bash
python -m pip install -r requirements.txt

# End-to-end-Lauf. Ohne Kaggle-Token nutzt der Kaggle-Adapter automatisch die
# mitgelieferten Demo-CSVs unter data/kaggle/ (lokaler Fallback).
python -m keeper_data.run

# Nur eine Quelle ausführen (z.B. beim Bootstrap):
python -m keeper_data.run --only kaggle_playerscores

# Tests:
python -m pytest -q
```

Ergebnis: gefüllte SQLite-DB (`keeper_data.db`) und statischer Export unter
`export/` (`feed.json`, `league/<code>.json`, `club/<club_id>.json`, `meta.json`
plus CSV-Spiegel des Feeds).

## Architektur

Adapter-Pattern: eine Ingestion-Schnittstelle, mehrere Quellen, gemeinsame
Normalisierung.

```
keeper_data/
  config.py              zentrale Konfiguration (config.yaml + .env)
  models.py / db.py      SQLAlchemy-Schema (SQLite -> Postgres) + Upserts
  http_client.py         höflicher HTTP-Client (Rate-Limit, robots.txt, Retries)
  sources/
    base.py              SourceAdapter (ABC) + RawRecord
    kaggle_playerscores  Basis-Historie (F-01) + lokaler CSV-Fallback
    tm_delta_scraper     tagesfrische Transfers (F-02)
    tm_youth_scraper     Nachwuchs (F-03)
  normalize.py           Roh -> kanonisches Schema, GK-Filter (F-04)
  change_detection.py    idempotente Persistenz + transfer_events (F-06)
  analytics/             Liga-/Klub-Trajektorien + Feed (§7)
  export.py              statischer JSON/CSV-Export (F-09)
  run.py                 Batch-Einstiegspunkt (F-10)
```

**Pipeline-Fluss** (`run.py`): Config → DB init → je Quelle
`fetch()` → `normalize()` (GK-Filter) → `change_detection()` (idempotent) →
`ingestion_runs` protokollieren → Analytics + Export. Fehlgeschlagene
Einzelquellen brechen den Gesamtlauf nicht ab (graceful degradation).

## Konfiguration

Alles zentral in [`config.yaml`](config.yaml); Secrets/Overrides in `.env`
(siehe [`.env.example`](.env.example)). Wichtig:

- **Quellen aktivieren/deaktivieren:** `sources.<name>.enabled`. Die beiden
  TM-Scraper sind standardmäßig **aus** — erst scharf schalten, wenn die
  Selektoren gegen die aktuelle TM-Struktur verifiziert sind (die HTML-Struktur
  kann sich ändern; die Parse-Logik ist gegen Fixtures in `tests/` getestet).
- **Kaggle:** mit `KAGGLE_USERNAME`/`KAGGLE_KEY` wird der Datensatz
  `davidcariboo/player-scores` via `kagglehub` geladen; ohne Token greift der
  CSV-Fallback aus `sources.kaggle_playerscores.local_csv_dir`.
- **DB:** `database.url` (Default SQLite) oder `DATABASE_URL` in `.env`
  (z.B. Free-Tier-Postgres bei Supabase/Neon).
- **Politeness (NF-02):** `http.min_delay_seconds`, `max_retries`,
  `respect_robots_txt`, `user_agent`.

## Datenquellen & Recht (NF-03)

Es werden **keine Transfermarkt-Marktwerte** übernommen und **keine rohen
Fremd-Tabellen** veröffentlicht — nur eigene Aggregationen (Entwicklungskurven,
Pfad-Analysen) und Transfer-*Fakten*. Jeder Datensatz trägt `source` und
`ingested_at` (NF-08); der Export enthält eine Quellenattribution (`meta.json`).

## Scheduling

Täglicher Lauf via GitHub Actions:
[`.github/workflows/daily.yml`](.github/workflows/daily.yml). Der Export wird als
Artefakt hochgeladen und optional ins Repo committet (für GitHub Pages).
Kaggle-Zugang als Repo-Secrets `KAGGLE_USERNAME`/`KAGGLE_KEY` hinterlegen.

## Tests

`pytest` deckt Normalisierung/GK-Filter, Change-Detection-**Idempotenz**,
Adapter (Kaggle-CSV + TM-HTML-Fixtures) sowie Analytics und einen
End-to-End-Export ab.
