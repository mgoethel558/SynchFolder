# Funktionale Spezifikation: Fit-to-Standard Outcome Dashboard

| Eigenschaft | Angabe |
|---|---|
| Dokumentstatus | Entwurf zur Abstimmung |
| Stand | 06.10.2026 |
| Autor | Claude Code |
| Zielgruppe | Projektleitung, Workstream Leads, Status-Meeting-Teilnehmer |
| Geltungsbereich | Lokales HTML-Dashboard zur Auswertung der F2S-Workshop-Outcome-Dateien aus SharePoint (lesend). Snapshot-Historie als JSON. |

---

## Inhaltsverzeichnis

1. Management Summary
2. Ausgangslage und Ziele
3. Leitprinzipien
4. Zielarchitektur
5. Daten-Mapping
6. Snapshot-Datenmodell und Historie
7. Verzeichnisstruktur
8. Ablauf „Aktualisieren"
9. Dashboard-Layout und Grafiken
10. Sprache (DE/EN)
11. PDF-Export
12. Konfiguration (Mapping)
13. Nicht-funktionale Anforderungen
14. Fehlerbehandlung und Robustheit
15. Weitergabe als eigenständiges Paket
16. Akzeptanzkriterien
17. Risiken und Gegenmaßnahmen
18. Roadmap
19. Offene Punkte
- Anhang A: Beispiel Snapshot-JSON
- Anhang B: Beispiel Mapping-Konfiguration

---

## 1. Management Summary

Im Projekt werden Fit-to-Standard-Workshops (SAP S/4HANA Cloud Public Edition) durchgeführt. Die Ergebnisse jedes Workshops liegen als Excel-Datei (`F2S_Workshop_Outcome_*.xlsx`) in einem SharePoint-Ordner. Ziel ist ein **lokales HTML-Dashboard**, das diese Dateien per Knopfdruck lädt, auswertet, die Ergebnisse historisiert und für Status-Meetings aufbereitet.

Der Ansatz trennt sauber zwischen **Datenbeschaffung** (vorhandene Python-Download-Funktion, rein lesender SharePoint-Zugriff), **Aggregation** (Python-Backend) und **Darstellung** (statisches HTML, offline lauffähig). Jeder Lauf schreibt einen **Snapshot** in eine fortlaufende JSON-Datei; das Dashboard rendert immer aus dieser JSON und funktioniert daher auch ohne Excel-Dateien und nach einem Neustart.

**Kernentscheidungen:**

- Datenbeschaffung über die **vorhandene** Download-Funktion ([sp_downloader.py](../Temp/SP_Downloader_Paket/sp_downloader.py)) — ausschließlich lesend. Auf SharePoint wird nichts geschrieben, verschoben oder gelöscht.
- Ein **minimales lokales Python-Backend** (Flask-frei, nur `http.server` aus der Standardbibliothek) stellt dem Browser den „Aktualisieren"-Endpunkt bereit, weil ein Browser aus Sicherheitsgründen keine lokalen Python-Downloads anstoßen kann.
- Historie als **append-only JSON** — Snapshots werden nie überschrieben.
- Mapping (Spaltennamen, Status-Zuordnung) liegt in einer **Konfigurationsdatei**, nicht im Code.
- Chart-Bibliothek wird **lokal** eingebunden (offline).
- Das Dashboard wird als **eigenständiges, weitergabefähiges Paket** ausgeliefert (portable Python, Browser beim ersten Start), sodass eine Kollegin / ein Kollege es ohne Vorinstallation genauso ausführen kann (siehe Kapitel 15).

---

## 2. Ausgangslage und Ziele

### 2.1 Ausgangslage

- Pro Workshop existiert eine Excel-Datei mit drei Sheets: `Workshop Summary` (Metadaten), `Outcome Log` (Einträge), `Dropdown Lists` (Wertelisten).
- Die Dateien liegen in einem SharePoint-Ordner und werden mit `F2S` als Namenspräfix geführt.
- Eine Python-Download-Funktion mit interaktiver Browser-Authentifizierung ist bereits vorhanden und getestet.

### 2.2 Ziele

- Alle F2S-Outcome-Dateien eines SharePoint-Ordners reproduzierbar laden und aggregieren.
- Ergebnisse pro Workstream / Line of Business (LoB) sowie als Gesamtzahlen darstellen.
- Verlauf über die Zeit sichtbar machen (Burn-up aus Snapshot-Historie).
- Für Status-Meetings optimierte Grafiken und eine sortierbare Tabelle bereitstellen.
- Vollständig lokal, offline-fähig, mit DE/EN-Umschaltung und sauberem PDF-Export.

### 2.3 Abgrenzung

- **Kein** Schreibzugriff auf SharePoint, keine Veränderung der Quelldateien.
- Keine Cloud-Dienste, keine externen CDNs, keine Telemetrie.
- Phase 1 wertet die vorhandene Dateistruktur aus; eine „geplant"-Dimension für Workshops ist nicht Teil (siehe Offene Punkte).

---

## 3. Leitprinzipien

| Prinzip | Bedeutung |
|---|---|
| Lesend auf der Quelle | SharePoint wird ausschließlich gelesen. Temporäre Excel-Kopien werden lokal verarbeitet und nach jedem Lauf gelöscht (try/finally). |
| Snapshots statt Live-Zustand | Das Dashboard rendert aus der JSON-Historie, nicht direkt aus Excel. Jeder Lauf ist mit Zeitstempel nachvollziehbar. |
| Deterministische Aggregation | Alle Kennzahlen werden durch Code aus den Zellwerten berechnet, nachvollziehbar und ohne freie Interpretation. |
| Nichts stillschweigend verwerfen | Unbekannte Status-/Typwerte und leere Pflichtzellen werden geloggt und separat ausgewiesen. |
| Konfiguration statt Code | Spaltennamen und Status-Zuordnungen stehen in einer Mapping-Datei und sind ohne Code-Änderung anpassbar. |
| Offline-fähig | Alle Ressourcen (Chart-Bibliothek, Fonts) liegen lokal. Keine Internetverbindung außer dem lesenden SharePoint-Download nötig. |

---

## 4. Zielarchitektur

### 4.1 Überblick

```
SharePoint (nur lesend)
   │  vorhandene Download-Funktion (Playwright + REST-API)
   ▼
Temp-Ordner  (F2S_*.xlsx, wird nach jedem Lauf geleert)
   │  Parser + Aggregator (Python, openpyxl)
   ▼
snapshots.json  (append-only Historie)
   │  liest
   ▼
Dashboard (index.html + lokale Chart-Lib)  ◄── lokaler HTTP-Server (http.server)
                                               stellt /api/refresh + statische Dateien bereit
```

### 4.2 Komponenten

| Komponente | Aufgabe |
|---|---|
| `sp_downloader.py` (vorhanden) | Lädt F2S-Excel-Dateien lesend aus SharePoint in den Temp-Ordner. Wird als Modul importiert, nicht neu geschrieben. |
| `backend.py` | Lokaler HTTP-Server (Standardbibliothek). Endpunkte: `GET /` (Dashboard), `POST /api/refresh` (Download→Parse→Aggregate→Snapshot→Cleanup), `GET /api/snapshots` (liefert JSON). |
| `parser.py` | Liest `Workshop Summary` + `Outcome Log`, normalisiert Werte anhand der Mapping-Konfiguration. |
| `aggregate.py` | Bildet Aggregate pro LoB und die Eintragsliste pro Snapshot. |
| `mapping.config.json` | Spaltennamen, Status-Zuordnungen, Typ-Definitionen. Frei anpassbar. |
| `index.html` | Dashboard: Header, Grafiken, KPIs, Tabelle, DE/EN, PDF-Export. |
| `assets/` | Lokale Chart-Bibliothek, Fonts, CSS. |
| `snapshots.json` | Append-only Historie. |
| `START_DASHBOARD.bat` | Startet das Backend per Doppelklick und öffnet den Browser. |

**Warum ein Backend?** Ein Browser kann aus Sicherheitsgründen keinen lokalen Python-Prozess starten oder den SharePoint-Login-Browser öffnen. Der „Aktualisieren"-Button ruft daher `POST /api/refresh` auf dem lokalen Server auf. Der Server liegt vollständig auf dem Rechner des Nutzers; es verlassen keine Daten den Rechner.

---

## 5. Daten-Mapping

### 5.1 Quelle je Workshop (Sheet `Workshop Summary`, Schlüssel in Spalte B, Wert in Spalte C)

| Feld | Zelle | Verwendung im Dashboard |
|---|---|---|
| Workshop ID | C6 | eindeutige Workshop-Kennung (z. B. `R2R-CO-33`) |
| Workshop Title | C7 | Anzeige/Tooltip |
| **Workstream** | C8 | **Primär-Gruppierung (LoB)** |
| Area | C9 | optionale zweite Ebene |
| Scope Item(s) | C10 | Anzeige |
| Date | C11 | Workshop-Datum |
| Overall Result | C17 | **Workshop „durchgeführt" wenn gefüllt** |
| Approval Status | C24 | Anzeige/Tooltip |

### 5.2 Quelle je Eintrag (Sheet `Outcome Log`, Header Zeile 4, Daten ab Zeile 5)

| Spalte | Feld | Verwendung |
|---|---|---|
| A | Outcome ID | **eindeutige Eintrags-ID** für Snapshot-Tracking |
| B | Record Type | Requirement / Issue / Assumption / Information |
| H | Fit Assessment | Status-Ableitung für Requirement/Issue |
| O | Decision | **Decision zählt nur, wenn dieses Feld gefüllt ist** |
| P | Decision Status | Status der Decision |
| R | Action | **Task zählt nur, wenn dieses Feld gefüllt ist** |
| U | Action Status | Status des Tasks |
| T | Due Date | Anzeige (kein Abschlussdatum) |

### 5.3 Typ-Zählung (entspricht der getroffenen Entscheidung)

Eine Outcome-Log-Zeile kann **mehrere** Zähl-Objekte erzeugen:

- **Requirement**: wenn `Record Type == "Requirement"`.
- **Issue**: wenn `Record Type == "Issue"`.
- **Assumption / Information**: werden gezählt und geloggt, in KPIs/Grafiken nachrangig.
- **Decision**: wenn Spalte O (`Decision`) **nicht leer** ist — unabhängig vom Record Type.
- **Task**: wenn Spalte R (`Action`) **nicht leer** ist — unabhängig vom Record Type.

### 5.4 Status-Normalisierung → `offen / in Arbeit / erledigt`

**Task** (aus `Action Status`, Spalte U):

| Excel-Wert | normalisiert |
|---|---|
| Open | offen |
| In Progress | in Arbeit |
| Blocked | in Arbeit |
| Closed | erledigt |
| Not Required / leer | (Task zählt nicht, da nur bei gefülltem Action-Feld) |

**Decision** (aus `Decision Status`, Spalte P):

| Excel-Wert | normalisiert |
|---|---|
| Decision Pending | offen |
| Approved | erledigt |
| Rejected | erledigt |
| Not Required / leer | (Decision zählt nicht, da nur bei gefülltem Decision-Feld) |

**Requirement / Issue** (aus `Fit Assessment`, Spalte H — gemäß Entscheidung):

| Excel-Wert | normalisiert |
|---|---|
| Open / To Be Assessed | offen |
| Fit | erledigt |
| Fit with Configuration | erledigt |
| Fit with Process Change | erledigt |
| Gap / Extension Required | erledigt (= bewertet) |
| Out of Scope | erledigt (= bewertet) |
| leer | unbekannt (geloggt, separat ausgewiesen) |

> Hinweis: „erledigt" bedeutet bei Requirement/Issue **bewertet** (Fit Assessment gesetzt), nicht zwingend „abgeschlossen". Die Zusatzgrafik Fit-Verteilung (9.2, Grafik D) zeigt die fachlich wichtigere Differenzierung Fit vs. Gap.

Alle Status-Zuordnungen stehen in `mapping.config.json`. **Unbekannte Werte** (nicht in der Liste) werden auf `unbekannt` abgebildet, geloggt und im Dashboard separat sichtbar gemacht — nie stillschweigend verworfen.

### 5.5 Workshop „durchgeführt"

Ein Workshop zählt als durchgeführt, sobald `Overall Result` (C17) **gefüllt** ist. Es gibt keine „geplant"-Quelle in den Dateien; Grafik C zeigt daher nur durchgeführte Workshops pro LoB.

---

## 6. Snapshot-Datenmodell und Historie

### 6.1 Prinzip

- Jeder „Aktualisieren"-Lauf erzeugt **einen** Snapshot mit UTC-Zeitstempel und hängt ihn an `snapshots.json` an. **Nie überschreiben.**
- Das Dashboard liest ausschließlich `snapshots.json`.

### 6.2 Pro Snapshot gespeichert

- `timestamp` (ISO-8601), `run_id`, Zahl verarbeiteter Dateien, Liste geladener Workshop-IDs, Liste von Warnungen (unbekannte Werte etc.).
- **Aggregate pro LoB**: je Typ (Requirement/Issue/Task/Decision) die Zählung nach `offen/in Arbeit/erledigt/unbekannt`, Workshops durchgeführt, Fit-Assessment-Verteilung.
- **Pro Eintrag**: `outcome_id`, `typ`, `lob`, `status` (falls vorhanden), zugehörige `workshop_id`. Damit sind Neuanlagen und Abschlüsse über die Zeit nachvollziehbar (Grundlage für Burn-up).

### 6.3 Identische Folge-Snapshots

Wenn ein Lauf **inhaltlich identisch** zum letzten Snapshot ist (gleiche Eintrags-IDs mit gleichem Status, gleiche Aggregate), wird er dennoch gespeichert, aber mit `"unchanged": true` **markiert**. Grafik A kann so markierte Punkte optional zusammenfassen; die KPIs/Tabelle zeigen immer den jüngsten Snapshot. So wächst die Historie nachvollziehbar, ohne die Verlaufskurve mit Dubletten zu verfälschen.

### 6.4 Burn-up-Ableitung (Grafik A)

Mangels Erstell-/Abschlussdatum pro Eintrag wird der Verlauf aus der Snapshot-Historie gebildet:

- **angelegt (kumuliert)**: ein Eintrag gilt ab dem ersten Snapshot als angelegt, in dem seine `outcome_id` auftaucht.
- **geschlossen (kumuliert)**: ein Eintrag gilt ab dem ersten Snapshot als geschlossen, in dem sein Status `erledigt` ist.

---

## 7. Verzeichnisstruktur

```
F2S_Dashboard/
├── SPEZIFIKATION.md            dieses Dokument
├── README.md                   Start, Aktualisieren, Ablageorte, Mapping anpassen
├── START_DASHBOARD.bat         Backend starten + Browser öffnen (Doppelklick)
├── backend.py                  lokaler HTTP-Server + Refresh-Orchestrierung
├── parser.py                   Excel → normalisierte Einträge
├── aggregate.py                Einträge → Aggregate pro LoB + Snapshot
├── mapping.config.json         Spaltennamen + Status-Zuordnung (anpassbar)
├── index.html                  Dashboard (Darstellung)
├── assets/
│   ├── chart.min.js            lokale Chart-Bibliothek (offline)
│   ├── app.js                  Rendering, DE/EN, PDF-Export
│   ├── i18n.js                 zentrale Übersetzungsdatei DE/EN
│   └── style.css               Design (aus Design-Vorlage übernommen)
├── data/
│   └── snapshots.json          append-only Historie
└── temp/                       temporäre Excel-Downloads (nach Lauf leer)
```

---

## 8. Ablauf „Aktualisieren"

Ausgelöst durch den Button; Backend-Endpunkt `POST /api/refresh`:

1. **Download**: F2S-Excel-Dateien über die vorhandene Download-Funktion in `temp/` laden (lesend von SharePoint).
2. **Parsen & Aggregieren**: Jede Datei parsen (`parser.py`), Werte normalisieren, Aggregate bilden (`aggregate.py`).
3. **Snapshot anhängen**: Ergebnis mit Zeitstempel an `data/snapshots.json` **anhängen** (nie überschreiben); ggf. `unchanged`-Markierung.
4. **Antwort**: Backend liefert Status + Warnungen an den Browser; Dashboard rendert neu.
5. **Cleanup (try/finally)**: Alle Dateien in `temp/` werden gelöscht — **auch bei Fehlern** in Schritt 1–3.

**Weitere Anforderungen:**

- **Statusanzeige** während des Laufs (Spinner + Phasentext: „Lade Dateien…", „Werte aus…", „Speichere Snapshot…").
- **Verständliche Fehlermeldung** bei Download-/Parsing-Fehler (konkrete Ursache, keine Stacktraces im UI).
- **Zeitstempel „Letzte Aktualisierung"** im Header, aus dem jüngsten Snapshot.
- SharePoint bleibt **unverändert** (nur lesende REST-Aufrufe).

---

## 9. Dashboard-Layout und Grafiken

### 9.1 Layout (von oben nach unten)

1. **Header**: Titel, „Letzte Aktualisierung", Button „Aktualisieren", Button „PDF-Export", DE/EN-Umschalter oben rechts.
2. **Grafik-Sektion** (Grafiken A–D).
3. **KPI-Zusammenfassung**: Gesamtzahlen Workshops, Requirements, Issues, Tasks, Decisions — je mit Anteil erledigt.
4. **Tabelle pro Workstream / LoB**: sortierbar, mit Summenzeile.

### 9.2 Grafiken

| Grafik | Inhalt | Begründung |
|---|---|---|
| **A — Burn-up (Verlauf)** | Kumuliert angelegt vs. geschlossen über die Snapshot-Zeit, je Typ umschaltbar. | Zeigt Fortschritt und Resttempo über mehrere Status-Meetings. |
| **B — Status pro LoB** | Gestapelte Balken pro LoB, je Typ aufgeteilt nach offen/in Arbeit/erledigt. | Direkter Soll-Blick fürs Status-Meeting: wo stauen sich offene Punkte? |
| **C — Workshop-Fortschritt pro LoB** | Anzahl durchgeführter Workshops je LoB. | Überblick, welche LoB wie weit im F2S-Prozess ist. |
| **D — Fit-Assessment-Verteilung pro LoB** *(Vorschlag)* | Fit / Fit w. Config / Fit w. Process Change / Gap / Open je LoB. | Fachlich zentralste F2S-Kennzahl: Standard-Grad vs. Gaps. Ergänzt die reine Statussicht. |

### 9.3 KPI-Zusammenfassung

Fünf KPI-Karten: Workshops (durchgeführt), Requirements, Issues, Tasks, Decisions — je Gesamtzahl + Anteil erledigt (%). Assumption und Information erhalten **keine** eigenen KPI-Karten (erscheinen nur in der Tabelle).

### 9.4 Tabelle pro LoB

Spalten: LoB · Workshops durchgeführt · Requirements (offen/in Arbeit/erledigt) · Issues (…) · Tasks (…) · Decisions (…). Sortierbar per Klick, mit **Summenzeile**. Unbekannt-Werte als separate, dezente Markierung.

Jede LoB-Zeile ist **aufklappbar**: Beim Aufklappen erscheint eine zweite Ebene mit den **Areas** dieser LoB (gleiche Spaltenstruktur). Assumption und Information werden hier als zusätzliche, dezente Spalte/Angabe mitgeführt, damit sie nicht verloren gehen.

---

## 10. Sprache (DE/EN)

- Alle Texte, Labels, Achsen und Statuswerte über eine **zentrale Übersetzungsdatei** `assets/i18n.js` (Schlüssel → {de, en}).
- Umschalter oben rechts (Muster aus Design-Vorlage: `body.lang-de/en` + `localStorage`).
- Auswahl wird in `localStorage` **gemerkt**; Default aus Browsersprache.
- Auch die normalisierten Statuswerte (offen/in Arbeit/erledigt) und Typnamen sind übersetzt.

---

## 11. PDF-Export

- Button erzeugt ein sauberes PDF **ohne externe Dienste**.
- Umsetzung: **Print-Stylesheet** (`@media print`) — A4 **Querformat** (`@page { size: A4 landscape }`), Grafiken nicht abgeschnitten (`break-inside: avoid`), Header mit Datum, Bedienelemente ausgeblendet.
- Auslösung clientseitig über `window.print()`; der Nutzer wählt „Als PDF speichern".

---

## 12. Konfiguration (Mapping)

`mapping.config.json` enthält:

- **Dateinamen-Präfix** der Outcome-Dateien (`F2S`).
- **Sheet-Namen** (`Workshop Summary`, `Outcome Log`).
- **Zell-/Spaltenzuordnung** (z. B. Workstream = Summary C8; Record Type = Log Spalte B).
- **Status-Zuordnungstabellen** (Action/Decision/Fit → offen/in Arbeit/erledigt).
- **Typ-Definitionen** und Zählregeln (Decision/Task nur bei gefülltem Feld).

Änderungen hier wirken ohne Code-Anpassung. Unbekannte Werte werden gegen diese Tabellen geprüft und bei Nichttreffer als `unbekannt` geloggt.

---

## 13. Nicht-funktionale Anforderungen

- Läuft vollständig lokal; keine Daten verlassen den Rechner außer dem lesenden SharePoint-Zugriff.
- Chart-Bibliothek und Fonts lokal eingebunden (offline-fähig).
- Robust gegen leere Zellen, unbekannte Statuswerte, zusätzliche Spalten (werden ignoriert, aber geloggt).
- Mapping in Konfigurationsdatei, nicht hart codiert.
- README mit Start, Aktualisieren, Ablageorten (temp, JSON) und Mapping-Anpassung.
- Design (Farben, Typografie, Komponenten, Umschalter) aus der Design-Vorlage übernommen.

---

## 14. Fehlerbehandlung und Robustheit

- **Download-Fehler** (Login-Timeout, kein Zugriff): klare Meldung, kein Snapshot, Temp-Cleanup trotzdem.
- **Parsing-Fehler** einer einzelnen Datei: Datei wird übersprungen, Warnung gesammelt, übrige Dateien werden verarbeitet.
- **Unbekannte Status-/Typwerte**: auf `unbekannt` gemappt, in `warnings` des Snapshots und im UI sichtbar.
- **Leeres `snapshots.json`** (Erststart): Dashboard zeigt leeren Zustand mit Hinweis „Noch keine Daten — bitte Aktualisieren".
- **Temp-Cleanup** immer in `finally`, auch bei Abbruch.

---

## 15. Weitergabe als eigenständiges Paket

Das Dashboard muss von einer Kollegin / einem Kollegen **ohne Vorinstallation** genauso ausführbar sein wie auf dem Rechner des Autors. Dafür wird dasselbe erprobte Paket-Muster wie beim SharePoint-Downloader verwendet.

### 15.1 Paketinhalt

```
F2S_Dashboard_Paket/
├── START_DASHBOARD.bat        Doppelklick: Browser-Setup (1. Start) → Backend → Browser öffnen
├── LIESMICH.txt               Kurzanleitung + Datenschutzhinweise
├── python/                    portable Python 3.12 (embeddable) inkl. playwright, openpyxl
├── app/                       backend.py, parser.py, aggregate.py, mapping.config.json
│   ├── index.html
│   └── assets/                chart.min.js, app.js, i18n.js, style.css (alles lokal)
├── data/
│   └── snapshots.json         wächst beim Nutzer; im Auslieferungszustand leer oder nicht vorhanden
└── temp/                      leer
```

### 15.2 Portabilität (Muster aus dem Downloader-Paket)

- **Portable Python 3.12** (Windows embeddable) ist im Paket enthalten — keine System-Installation nötig.
- **Playwright-Browser** wird **beim ersten Start** einmalig heruntergeladen (ca. 170 MB, benötigt einmalig Internet) und nach `%LOCALAPPDATA%\F2S-Dashboard\ms-playwright` gelegt — **nicht** in den Paketordner, damit OneDrive-/SharePoint-Synchronisierung die Datei-Locks nicht stört.
- Die **SharePoint-Login-Session** liegt ebenfalls unter `%LOCALAPPDATA%\F2S-Dashboard\.pw-profile` — benutzerbezogen. So wird beim Weitergeben **nie eine fremde Sitzung** mitgegeben; jede Person meldet sich mit dem eigenen Konto an und sieht nur, worauf sie Zugriff hat.
- Start per **Doppelklick** auf `START_DASHBOARD.bat`: richtet beim ersten Mal den Browser ein, startet dann das lokale Backend und öffnet das Dashboard im Standardbrowser.

### 15.3 Sicherheit / Datenschutz bei Weitergabe

- Es werden **keine Zugangsdaten** im Paket gespeichert oder mitgeliefert.
- Vor der Weitergabe werden `data/snapshots.json` (enthält Projektdaten) und die Login-Session **nicht** mitgegeben, sofern der Nutzer eine „leere" Verteilversion wünscht; alternativ kann eine gefüllte `snapshots.json` bewusst mitgegeben werden, um die Historie zu teilen. Dies wird in der LIESMICH dokumentiert.
- Es wird ausschließlich lesend auf SharePoint zugegriffen; auf dem Zielrechner verlassen keine Daten den Rechner.

### 15.4 Konsequenz für die Entwicklung

Entwickelt wird zunächst im Projektordner `F2S_Dashboard/` (Kapitel 7). Das weitergabefähige Paket `F2S_Dashboard_Paket/` wird daraus gebaut, indem die portable Python-Umgebung (identisch zum Downloader-Paket) und der Launcher ergänzt werden. Backend, Parser und Dashboard bleiben identisch.

---

## 16. Akzeptanzkriterien

1. Nach „Aktualisieren" sind Zahlen in Tabelle, KPIs und Grafiken konsistent mit den Excel-Dateien.
2. Der Temp-Ordner ist danach leer — auch nach einem provozierten Fehler.
3. Auf SharePoint gibt es keinerlei Schreibzugriffe (nur `GET`-REST-Aufrufe).
4. `snapshots.json` wächst pro Lauf; Grafik A zeigt den Verlauf über mehrere Läufe.
5. Der DE/EN-Umschalter ändert alle Texte, Labels, Achsen und Statuswerte; Auswahl bleibt gemerkt.
6. Das PDF ist lesbar und vollständig (A4 quer, Grafiken nicht abgeschnitten, Header mit Datum).
7. Unbekannte Werte werden geloggt und sichtbar gemacht, nicht stillschweigend verworfen.
8. Das Dashboard rendert aus der JSON auch ohne Excel-Dateien und nach einem Neustart.
9. Das weitergegebene Paket startet auf einem anderen Rechner per Doppelklick, ohne Python-Vorinstallation; der erste Start richtet den Browser ein, danach ist kein Internet außer dem SharePoint-Zugriff nötig.

---

## 17. Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| SharePoint-Login läuft ab | Playwright-Session persistiert; klare Meldung bei Timeout; erneuter Login im sichtbaren Browser. |
| Excel-Struktur ändert sich | Mapping-Konfiguration + Logging unbekannter Spalten/Werte; Datei-weises Überspringen statt Abbruch. |
| Keine Erstell-/Abschlussdaten pro Eintrag | Burn-up aus Snapshot-Historie; früher und regelmäßig aktualisieren, damit die Kurve aussagekräftig wird. |
| OneDrive-Sync stört lokale Dateien | Backend/Temp liegen im Projektordner; empfohlene Ablage außerhalb aktiver Sync-Konflikte (README-Hinweis). |

---

## 18. Roadmap

- **Phase 1** (diese Spezifikation): Download, Aggregation, Snapshot-Historie, Dashboard, DE/EN, PDF, weitergabefähiges Paket.
- **Phase 2** (freigegeben als Ausblick): **„geplant"-Dimension pro LoB** (Grafik C um durchgeführt-vs-geplant erweitern, Soll-Werte aus Config oder separater Planungsliste), Drill-down auf Eintragsebene, Export der Tabelle als Excel/CSV, Filter nach Area/Country, Area als aufklappbare zweite Tabellenebene.

---

## 19. Offene Punkte

Alle zuvor offenen Punkte sind entschieden:

- „geplant" (Grafik C): **in Phase 2** umgesetzt; Phase 1 zeigt nur durchgeführt.
- Assumption/Information: erscheinen **nur in der Tabelle**, keine eigenen KPI-Karten.
- Area-Ebene als aufklappbare zweite Tabellenebene: **wird so umgesetzt**.

---

## Anhang A: Beispiel Snapshot-JSON (gekürzt)

```json
{
  "snapshots": [
    {
      "timestamp": "2026-10-06T08:15:00Z",
      "run_id": "20261006-081500",
      "files_processed": 2,
      "workshop_ids": ["R2R-CO-33", "R2R-CO-36"],
      "unchanged": false,
      "warnings": [
        {"file": "R2R-CO-33", "type": "unknown_status", "value": "On Hold", "column": "Action Status"}
      ],
      "lob_aggregates": {
        "Record-to-Report": {
          "workshops_conducted": 2,
          "requirement": {"offen": 1, "in Arbeit": 0, "erledigt": 3, "unbekannt": 0},
          "issue":       {"offen": 0, "in Arbeit": 1, "erledigt": 1, "unbekannt": 0},
          "task":        {"offen": 2, "in Arbeit": 1, "erledigt": 0, "unbekannt": 0},
          "decision":    {"offen": 0, "in Arbeit": 0, "erledigt": 2, "unbekannt": 0},
          "fit_assessment": {"Fit": 1, "Fit with Configuration": 2, "Gap / Extension Required": 1}
        }
      },
      "entries": [
        {"outcome_id": "R2R-CO-33-001", "typ": "requirement", "lob": "Record-to-Report", "status": "erledigt", "workshop_id": "R2R-CO-33"},
        {"outcome_id": "R2R-CO-33-001", "typ": "decision",    "lob": "Record-to-Report", "status": "erledigt", "workshop_id": "R2R-CO-33"},
        {"outcome_id": "R2R-CO-33-001", "typ": "task",        "lob": "Record-to-Report", "status": "offen",    "workshop_id": "R2R-CO-33"}
      ]
    }
  ]
}
```

## Anhang B: Beispiel Mapping-Konfiguration (gekürzt)

```json
{
  "file_prefix": "F2S",
  "sheets": {"summary": "Workshop Summary", "log": "Outcome Log"},
  "summary_cells": {"workshop_id": "C6", "workstream": "C8", "area": "C9", "date": "C11", "overall_result": "C17"},
  "log_header_row": 4,
  "log_columns": {
    "outcome_id": "A", "record_type": "B", "fit_assessment": "H",
    "decision": "O", "decision_status": "P", "action": "R", "action_status": "U", "due_date": "T"
  },
  "count_rules": {"decision_if_field": "decision", "task_if_field": "action"},
  "status_maps": {
    "action_status": {"Open": "offen", "In Progress": "in Arbeit", "Blocked": "in Arbeit", "Closed": "erledigt"},
    "decision_status": {"Decision Pending": "offen", "Approved": "erledigt", "Rejected": "erledigt"},
    "fit_assessment": {
      "Open / To Be Assessed": "offen", "Fit": "erledigt", "Fit with Configuration": "erledigt",
      "Fit with Process Change": "erledigt", "Gap / Extension Required": "erledigt", "Out of Scope": "erledigt"
    }
  },
  "unknown_value": "unbekannt"
}
```
