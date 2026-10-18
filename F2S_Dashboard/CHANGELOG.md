# Änderungshistorie – F2S Outcome Dashboard

## v1.1.0 (06.10.2026)

**Neue Funktionen**
- **Drill-down:** Klick auf eine Zahl/Pill in der Tabelle öffnet eine
  Detailliste der dahinterliegenden Einträge (Outcome ID, Thema/Prozessschritt,
  Status, Verantwortlich, Fällig, Workshop-Name, Workshop-Datum) inklusive
  Link zur Quell-Excel in SharePoint.
- **Versionsanzeige** unten im Dashboard.

**Geänderte Zählung (wichtig)**
- **Jede Excel-Zeile zählt genau einmal** nach Record Type
  (Requirement/Issue/Assumption/Information). Eindeutigkeit über
  Datei + Outcome-ID (behebt Doppelzählung bei gleichen IDs in mehreren Dateien).
- **Tasks und Decisions** sind keine eigenen Zählobjekte mehr, sondern
  Attribute der Zeile. In KPIs/Tabelle als „offen von gesamt" dargestellt.

**Snapshot-Verhalten**
- Ein neuer Snapshot wird **nur noch bei inhaltlicher Änderung** angehängt.
  Mehrfaches Ausführen am selben Tag erzeugt keine Dubletten mehr in der Historie.

**Verteilung**
- Updates können als kleines **Update-ZIP** (~100 KB) verteilt werden
  (`build_update.py` → `F2S_Dashboard_Update_v<Version>.zip`). Kollegen spielen
  es per `UPDATE.bat` ein; Daten, portable Python und `config.local.json`
  bleiben erhalten. Kein erneutes 148-MB-Paket nötig.

## v1.0.0

- Erstversion: Download aus SharePoint (lesend), Aggregation, Snapshot-Historie,
  Dashboard (Grafiken A–D, KPIs, Tabelle), DE/EN, PDF-Export, weitergabefähiges
  Paket mit portabler Python.
