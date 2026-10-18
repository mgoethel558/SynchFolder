"""
aggregate.py -- Fasst geparste Workshops zu einem Snapshot zusammen.

Erzeugt:
  - Aggregate pro LoB (Workstream): je Typ die Zaehlung nach Status,
    Workshops durchgefuehrt, Fit-Assessment-Verteilung, Area-Unterebene.
  - flache Eintragsliste (fuer Burn-up ueber die Historie).
  - Warnungen (unbekannte Werte etc.).

Der Snapshot wird append-only in snapshots.json geschrieben; identische
Folge-Snapshots werden mit "unchanged": true markiert (nicht verworfen).
"""
from __future__ import annotations

import json
from pathlib import Path

# Status-Kategorien, die im Dashboard dargestellt werden.
STATUS_KEYS = ["offen", "in Arbeit", "erledigt", "nicht relevant", "unbekannt"]
# Zaehlmodell Variante B: Jede Excel-Zeile zaehlt genau EINMAL nach Record Type.
# Haupttypen mit eigener Status-Aufteilung (Tabelle/Grafik B/KPIs):
MAIN_TYPES = ["requirement", "issue"]
# Zusatztypen: nur in der Tabelle, keine KPI-Karten / Grafik-B-Stapel.
EXTRA_TYPES = ["assumption", "information", "unbekannt"]
ALL_TYPES = MAIN_TYPES + EXTRA_TYPES


def _empty_counts() -> dict:
    return {k: 0 for k in STATUS_KEYS}


def _empty_lob() -> dict:
    return {
        "workshops_conducted": 0,
        "workshop_ids": [],
        "counts": {t: _empty_counts() for t in ALL_TYPES},
        # Zeilen-Attribute (nicht eigene Zaehltypen): offene Tasks/Decisions
        "open_tasks": 0,
        "open_decisions": 0,
        "total_tasks": 0,
        "total_decisions": 0,
        "fit_assessment": {},
        "areas": {},
    }


def build_snapshot(parsed_list: list[dict], run_id: str, timestamp: str,
                   config: dict) -> dict:
    """parsed_list: Liste von parse_workbook()-Ergebnissen."""
    lob_aggregates: dict[str, dict] = {}
    entries_flat: list[dict] = []
    warnings: list[dict] = []
    workshop_ids: list[str] = []

    def ensure_lob(name: str) -> dict:
        if name not in lob_aggregates:
            lob_aggregates[name] = _empty_lob()
        return lob_aggregates[name]

    def ensure_area(lob: dict, name: str) -> dict:
        if name not in lob["areas"]:
            lob["areas"][name] = {
                "workshops_conducted": 0,
                "counts": {t: _empty_counts() for t in ALL_TYPES},
                "open_tasks": 0, "open_decisions": 0,
                "total_tasks": 0, "total_decisions": 0,
            }
        return lob["areas"][name]

    for parsed in parsed_list:
        ws = parsed["workshop"]
        warnings.extend(parsed.get("warnings", []))
        # Unausgefuellte Vorlagen-Kopien nicht mitzaehlen (bereits als Warnung
        # gemeldet). Verhindert z. B. einen Schein-Workshop "Lead-to-Cash".
        if ws.get("is_placeholder"):
            continue
        lob_name = ws.get("workstream") or config.get("unknown_value", "unbekannt")
        area_name = ws.get("area") or config.get("unknown_value", "unbekannt")
        # Workshop-ID fuer die Anzeige; eindeutige Zaehlung aber ueber die
        # Quelldatei (zwei Dateien koennen versehentlich dieselbe ID tragen).
        wsid = ws.get("workshop_id") or ws.get("source_file", "?")
        wskey = ws.get("source_file") or wsid
        workshop_ids.append(wsid)  # eine Datei = ein Eintrag (keine Dedup)

        lob = ensure_lob(lob_name)
        area = ensure_area(lob, area_name)

        if ws.get("conducted"):
            lob["workshops_conducted"] += 1
            area["workshops_conducted"] += 1
            if wskey not in lob["workshop_ids"]:
                lob["workshop_ids"].append(wskey)

        for e in parsed["entries"]:
            # Variante B: jede Zeile zaehlt genau einmal nach Record Type.
            typ = e["typ"]
            if typ not in ALL_TYPES:
                typ = "unbekannt"
            status = e.get("status", config.get("unknown_value", "unbekannt"))
            if status not in STATUS_KEYS:
                status = config.get("unknown_value", "unbekannt")

            lob["counts"][typ][status] = lob["counts"][typ].get(status, 0) + 1
            area["counts"][typ][status] = area["counts"][typ].get(status, 0) + 1

            # Task/Decision als Zeilen-ATTRIBUT aggregieren (keine eigene Zeile).
            if e.get("has_task"):
                lob["total_tasks"] += 1; area["total_tasks"] += 1
                if e.get("task_status") in ("offen", "in Arbeit"):
                    lob["open_tasks"] += 1; area["open_tasks"] += 1
            if e.get("has_decision"):
                lob["total_decisions"] += 1; area["total_decisions"] += 1
                if e.get("decision_status") == "offen":
                    lob["open_decisions"] += 1; area["open_decisions"] += 1

            # Fit-Assessment-Verteilung (nur Requirement/Issue tragen fit_assessment)
            fa = e.get("fit_assessment")
            if fa:
                lob["fit_assessment"][fa] = lob["fit_assessment"].get(fa, 0) + 1

            # flache Eintragsliste: Burn-up + Drill-down-Detailfelder.
            entries_flat.append({
                "uid": e.get("uid"),
                "outcome_id": e["outcome_id"],
                "typ": typ,
                "lob": lob_name,
                "area": area_name,
                "status": status,
                "workshop_id": wsid,
                "workshop_title": e.get("workshop_title", ""),
                "workshop_date": e.get("workshop_date", ""),
                "process_step": e.get("process_step", ""),
                "topic": e.get("topic", ""),
                "owner": e.get("owner", ""),
                "due_date": e.get("due_date", ""),
                "has_task": e.get("has_task", False),
                "task_status": e.get("task_status", ""),
                "has_decision": e.get("has_decision", False),
                "decision_status": e.get("decision_status", ""),
                "source_url": e.get("source_url", ""),
                "source_file": e.get("source_file", ""),
            })

    snapshot = {
        "timestamp": timestamp,
        "run_id": run_id,
        "files_processed": len(workshop_ids),  # ohne Platzhalter-Vorlagen
        "workshop_ids": workshop_ids,
        "warnings": warnings,
        "lob_aggregates": lob_aggregates,
        "entries": entries_flat,
    }
    return snapshot


def _signature(snapshot: dict) -> str:
    """Inhaltliche Signatur zum Erkennen identischer Folge-Snapshots
    (ignoriert timestamp/run_id). Nutzt die eindeutige uid je Eintrag."""
    key = {
        "lob": snapshot["lob_aggregates"],
        "entries": sorted(
            [(e.get("uid") or e["outcome_id"], e["typ"], e["status"],
              e.get("task_status", ""), e.get("decision_status", ""))
             for e in snapshot["entries"]]
        ),
    }
    return json.dumps(key, sort_keys=True, ensure_ascii=False)


def append_snapshot(snapshots_path: str | Path, snapshot: dict) -> tuple[dict, bool]:
    """Haengt den Snapshot nur an, wenn er sich inhaltlich vom letzten
    unterscheidet. Gibt (snapshot, appended) zurueck.
    appended=False -> es gab keine Aenderung, nichts wurde gespeichert."""
    snapshots_path = Path(snapshots_path)
    if snapshots_path.exists():
        with open(snapshots_path, encoding="utf-8") as f:
            store = json.load(f)
    else:
        store = {"snapshots": []}

    if store["snapshots"]:
        last = store["snapshots"][-1]
        if _signature(last) == _signature(snapshot):
            return snapshot, False  # keine Aenderung -> NICHT anhaengen

    store["snapshots"].append(snapshot)
    snapshots_path.parent.mkdir(parents=True, exist_ok=True)
    # Atomar schreiben: erst temp, dann ersetzen.
    tmp = snapshots_path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)
    tmp.replace(snapshots_path)
    return snapshot, True
