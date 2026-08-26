# SAP SSCUI Crawler – Dokumentation

**Verzeichnis:** `C:\Users\goeth\desktop\Crawling`  
**Stand:** Mai 2026  

---

## Übersicht

Das Crawling-Paket besteht aus zwei Programmen, die zusammen eine vollständige Datenbasis über alle SAP S/4HANA SSCUIs (System/4HANA Configuration UIs) erstellen:

| Schritt | Programm | Eingabe | Ausgabe |
|---------|----------|---------|---------|
| 1 | `cbc_crawler.py` | CBC-Webseite (live) | `sscui_export.xlsx` |
| 2 | `sscui_tech_crawler.py` | `sscui_export.xlsx` | `sscui_technical_info.xlsx` |

**Typischer Workflow:**

```
CBC-Portal → [cbc_crawler.py] → sscui_export.xlsx → [sscui_tech_crawler.py] → sscui_technical_info.xlsx
```

---

## 1. CBC Crawler (`cbc_crawler.py`)

### Was macht er?

Crawlt den Configuration-Tab des SAP CBC-Portals (Cloud Business Configuration) und extrahiert für jede SSCUI:
- **Name** (Anzeigebezeichnung)
- **Nummer** (eindeutige numerische ID)
- **Link** (direkte URL zur SAP S/4HANA WebGUI-Seite)

### Starten

```bash
cd C:\Users\goeth\desktop\Crawling
py cbc_crawler.py
```

**Mit Optionen:**

```bash
# Andere Ausgabedatei
py cbc_crawler.py -o meine_sscuis.xlsx

# Eigene Referenzliste für Vollständigkeitsprüfung
py cbc_crawler.py -r referenz.xlsx
```

### Parameter

| Parameter | Kurzform | Standard | Beschreibung |
|-----------|----------|----------|--------------|
| `--output` | `-o` | `sscui_export.xlsx` | Pfad der Ausgabe-Excel-Datei |
| `--reference` | `-r` | `Configure Your Business Processes(1).xlsx` | Referenzliste für Vollständigkeitsprüfung (Spalte A = SSCUI-Nummern) |

### Ablauf im Detail

#### Schritt 1 – Manueller Login
Das Programm öffnet einen sichtbaren Chromium-Browser und navigiert zur CBC-URL. Der Benutzer muss sich **manuell einloggen** (SSO/Passwort). Sobald die Configuration-Liste sichtbar ist, wird ENTER gedrückt.

#### Schritt 2 – Expand All
Das Programm sucht automatisch nach dem „Alle ausklappen"-Button (↓≡). Wenn er nicht automatisch gefunden wird, erscheint die Aufforderung, ihn manuell zu klicken.

#### Phase 1 – Scroll & Sammeln
Die CBC-Liste wird virtuell gerendert (nur sichtbare Zeilen im DOM). Das Programm scrollt **Schritt für Schritt** durch die gesamte Liste und sammelt bei jedem Scroll-Schritt alle sichtbaren Zeilen:
- Name aus `ui5-link` innerhalb von `span[data-testid^="titleTableCell_"]`
- ID aus `[data-column-id-cell="externalId"]`
- `testId` = eindeutiger Baumpfad-Selektor (z.B. `titleTableCell_1.2.3`)

Das Sammeln stoppt wenn 6 aufeinanderfolgende Schritte keine neuen SSCUIs liefern.

#### Phase 2 – URL-Ermittlung
Nach dem Sammeln werden die URLs durch Klick auf jeden Link ermittelt. Ein `window.open`-Interceptor fängt die URL ab ohne einen neuen Tab zu öffnen. Der `testId`-Selektor stellt sicher, dass auch nach Scroll-Positonsänderungen der richtige Link geklickt wird (kein Positions-Drift).

Bei fehlenden URLs werden bis zu **5 Passes** (Durchläufe von oben) durchgeführt.

#### Excel-Export
- Sheet **SSCUIs**: Alle gecrawlten Einträge
- Sheet **Fehlend** (wenn Referenzliste vorhanden): IDs die in der Referenz stehen aber nicht gecrawlt wurden
- Zeilen ohne URL: **gelb markiert**

### Ausgabe-Format (`sscui_export.xlsx`)

| Spalte | Beschreibung |
|--------|--------------|
| SSCUI Name | Vollständige Bezeichnung |
| SSCUI Nummer | Numerische ID |
| Link | Direkte SAP WebGUI URL |

### Bekannte Einschränkungen

- Benötigt **manuellen Login** (SSO kann nicht automatisiert werden)
- Bei sehr langen Listen (>500 Scroll-Schritte) wird das Limit erreicht; in diesem Fall den Expand-Button manuell klicken und warten bis alle Einträge geladen sind

---

## 2. SSCUI Technical Info Crawler (`sscui_tech_crawler.py`)

### Was macht er?

Öffnet jede SSCUI-URL aus der Export-Datei des CBC-Crawlers, identifiziert alle sichtbaren Felder per **Claude Vision AI**, drückt für jedes Feld **F1**, navigiert zu **Technical Information** und extrahiert die technischen Metadaten des Feldes.

### Starten

```bash
cd C:\Users\goeth\desktop\Crawling
py sscui_tech_crawler.py -i sscui_export.xlsx
```

**Mit Optionen:**

```bash
# Andere Ausgabedatei
py sscui_tech_crawler.py -i sscui_export.xlsx -o ergebnis.xlsx

# Ab Index 50 weitermachen (nach Abbruch)
py sscui_tech_crawler.py -i sscui_export.xlsx --start 50
```

### Parameter

| Parameter | Kurzform | Standard | Beschreibung |
|-----------|----------|----------|--------------|
| `--input` | `-i` | *(Pflichtfeld)* | Eingabe-Excel mit SSCUI Name, Nummer und URL |
| `--output` | `-o` | `sscui_technical_info.xlsx` | Ausgabe-Excel |
| `--start` | `-s` | `0` | Index ab dem gestartet wird (0-basiert, für Wiederaufnahme) |

### Voraussetzungen

#### API-Key
Der Anthropic API-Key muss in einer `.env`-Datei vorhanden sein. Das Programm sucht automatisch in:
1. `C:\Users\goeth\desktop\Crawling\.env`
2. `C:\Users\goeth\desktop\SAP_Config_Bot\.env`

Format der `.env`-Datei:
```
ANTHROPIC_API_KEY=sk-ant-...
```

#### Python-Pakete
```bash
py -m pip install playwright anthropic python-dotenv pillow openpyxl pandas
py -m playwright install chromium
```

### Ablauf im Detail

#### Schritt 1 – Manueller Login
Das Programm öffnet Chromium, navigiert zur ersten SSCUI-URL und wartet auf manuellen Login in S/4HANA. Nach erfolgreichem Login ENTER drücken.

#### Schritt 2 – iFrame-Erkennung
SAP WebGUI rendert die eigentliche Anwendung in `<iframe>`-Elementen ohne `src`-Attribut. Das Programm identifiziert automatisch den richtigen iFrame (denjenigen mit den meisten sichtbaren Input-Feldern) über JavaScript im Hauptseitenkontext mit `contentDocument`-Zugriff.

#### Schritt 3 – Felder identifizieren (Claude Vision)

**Primär: Claude Vision API**  
Das Programm macht einen Screenshot der geladenen Seite, komprimiert ihn auf max. 1280px JPEG (Qualität 85) und schickt ihn an `claude-sonnet-4-6`. Claude identifiziert alle sichtbaren Tabellenspalten bzw. Formularfelder und gibt Pixel-Koordinaten der ersten Datenzeile zurück:

```json
[
  {"label": "CCtC", "x": 150, "y": 320},
  {"label": "Name", "x": 280, "y": 320},
  {"label": "Qty",  "x": 410, "y": 320}
]
```

Koordinaten werden automatisch von Screenshot-Pixeln in Viewport-CSS-Pixel skaliert (HiDPI-kompatibel).

Gefilterte Spalten (werden übersprungen): `select`, `sel`, `sel.`, `selection`, `auswahl`, `row`, `zeile` – SAP-Zeilenauswahl-Spalten ohne Feldinformation.

**Fallback: DOM-Analyse**  
Falls die Vision API kein Ergebnis liefert, wird ein DOM-basierter Ansatz mit 3 Strategien verwendet:
1. Gleiche Tabelle mit Header-Zeile + Datenzeile
2. Getrennte Header/Daten-Tabellen (SAP Split-Table-Layout)
3. Formular-Ansicht mit Adjacent-Label-Erkennung

#### Schritt 4 – F1-Hilfe pro Feld

Für jedes identifizierte Feld:

1. **Klick** auf das Feld (Vision-Koordinaten)
2. **Value-Help-Check**: Falls durch den Klick ein SAP-Suchhilfe-Popup aufgeht (z.B. bei read-only Feldern wie CCtC), wird es mit Escape sofort geschlossen
3. **F1** drücken → SAP öffnet das F1-Hilfe-Popup
4. **"Technical Information"** klicken – gesucht wird ausschließlich innerhalb des sichtbaren Popups (verhindert Fehlklicks auf gleichnamige Elemente der Hauptseite)
5. **2,5 Sekunden warten** – Tech-Info-Popup vollständig laden lassen
6. **Daten extrahieren** (siehe unten)
7. **Popup schließen** über roten X-Button oder Escape

**Retry-Mechanismus:**  
Bei Fehlschlag wird ein zweiter Versuch gestartet – ohne erneuten Feldklick (verhindert Spalten-Drift durch SAP-Neurendering).

#### Schritt 5 – Daten extrahieren

Das Technical Information Popup hat eine feste Struktur mit immer denselben 8 Inputs in fester Reihenfolge. Die Werte werden per DOM-Reihenfolge (nicht per Label) extrahiert:

```
Input 0 → Screen - Program Name
Input 1 → Screen - Screen Number
Input 2 → GUI - Program Name
Input 3 → GUI - Status
Input 4 → Field - Table Name
Input 5 → Field - Field Name
Input 6 → Field - Data Element
Input 7 → Batch - Screen Field
```

SAP rendert die Werte in `<input readonly>`-Elementen – deshalb wird `input.value` statt `textContent` ausgelesen.

Das Popup wird in allen Dokumenten (Hauptseite + alle iFrames) gesucht. Erkannt wird es anhand von Schlüsselwörtern wie `Screen Number`, `Data Element`, `Field Name`, `Datenelement`, `Programm`, `Bildschirmdaten` etc.

#### Schritt 6 – Zwischenspeichern

Nach jeweils 10 SSCUIs wird automatisch zwischengespeichert. Bei gesperrter Ausgabedatei wird ein Timestamp-Suffix angehängt.

### Ausgabe-Format (`sscui_technical_info.xlsx`)

| Spalte | Beschreibung |
|--------|--------------|
| SSCUI Name | Name aus der Eingabedatei |
| SSCUI Nummer | Nummer aus der Eingabedatei |
| Screen | Seitentitel der SSCUI |
| Field Label | Spaltenname wie von Claude Vision erkannt |
| Screen - Program Name | ABAP-Programm des Screens |
| Screen - Screen Number | Dynpro-Nummer |
| GUI - Program Name | GUI-Programm |
| GUI - Status | GUI-Status |
| Field - Table Name | Datenbanktabelle |
| Field - Field Name | Datenbankfeldname |
| Field - Data Element | Data Element (ABAP Dictionary) |
| Batch - Screen Field | Batch-Input Feldname |

### Konsolenausgabe (Beispiel)

```
[1/1818] Define Cost Center Categories (102498)
  Content-Frame: iframe[0]  (2 Inputs gefunden)
  Screen: Define Cost Center Categories: Change
  [Vision] 7 Felder erkannt: ['Name', 'Qty', 'ActPri', 'ActSec', 'ActRev', 'Cmmt', 'Func']
  7 eindeutige Felder
  [ 1/7] 'Name' (col)... OK  (KOSAR)
  [ 2/7] 'Qty' (col)... OK  (KOSAR)
  ...
  → 7 Felder mit Tech-Info
```

---

## Technische Architektur

### Warum JavaScript im Hauptseiten-Kontext?

SAP WebGUI ITS rendert die Anwendung in `<iframe>`-Elementen ohne `src`-Attribut (dynamisch per JavaScript befüllt). Playwright's Frame-API kann diese iFrames nicht direkt adressieren, da sie keinen `src`-Selektor haben.

**Lösung:** Alle DOM-Operationen laufen im Hauptseiten-JavaScript-Kontext über `page.evaluate()`. Der Zugriff auf iFrame-Inhalte erfolgt via `iframe.contentDocument` – exakt wie in der Browser DevTools-Konsole.

Konsequenz: Alle Klick-Koordinaten müssen **main-page-relativ** berechnet werden:
```javascript
x = iframeBox.left + elementRect.left + elementRect.width / 2
y = iframeBox.top  + elementRect.top  + elementRect.height / 2
```

### Warum Claude Vision für Felder?

SAP WebGUI rendert Tabellen im „Split-Table-Layout": Header und Daten befinden sich in **separaten, verschachtelten Tabellen** innerhalb von `<td>`-Zellen. `textContent` des Parent-Elements liefert alle Spaltenüberschriften als einen zusammenhängenden String. Eine zuverlässige DOM-basierte Extraktion der einzelnen Spaltennamen ist damit nicht möglich.

Claude Vision analysiert den Screenshot und erkennt Spaltenbezeichnungen visuell – unabhängig von der HTML-Struktur.

### Warum feste Input-Reihenfolge bei Technical Information?

SAP rendert Labels mit dem ersten Zeichen in einem separaten `<span>`:
```html
<span>P</span><span>rogram Name</span>
```
→ `textContent` = `"P rogram Name"` (mit Leerzeichen)

Da das Technical Information Popup immer dieselbe Struktur mit denselben 8 Feldern in fester Reihenfolge hat, werden Inputs nach DOM-Position zugeordnet – das umgeht das Label-Split-Problem vollständig.

---

## Fehlerbehebung

### `ModuleNotFoundError: No module named 'playwright'`

```bash
py -m pip install playwright anthropic python-dotenv pillow openpyxl pandas
py -m playwright install chromium
```

### `ANTHROPIC_API_KEY nicht gefunden`

`.env`-Datei erstellen:
```
C:\Users\goeth\desktop\Crawling\.env
```
Inhalt:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Crawler stoppt bei SSCUI X – Wiederaufnahme

```bash
py sscui_tech_crawler.py -i sscui_export.xlsx --start X
```

### Ausgabedatei gesperrt (Excel offen)

Das Programm speichert automatisch unter neuem Namen mit Timestamp-Suffix:  
`sscui_technical_info_20260507_143022.xlsx`

### `kein F1-Popup` für bestimmte Felder

Mögliche Ursachen:
- Read-only Feld ohne F1-Hilfe in diesem SAP-Modus
- Klick-Koordinaten leicht daneben (Vision gibt Mittelpunkt der ersten Datenzeile zurück)
- SAP-Seite noch nicht vollständig geladen

Das Programm macht automatisch einen zweiten Versuch, danach wird das Feld übersprungen.

### `[Vision] JSON-Parsing fehlgeschlagen`

Selten – Claude hat kein valides JSON zurückgegeben. Das Programm fällt auf DOM-Analyse zurück.

---

## Datei-Übersicht

```
C:\Users\goeth\desktop\Crawling\
├── cbc_crawler.py               # CBC SSCUI Crawler (Schritt 1)
├── sscui_tech_crawler.py        # Technical Info Crawler (Schritt 2)
├── sscui_export.xlsx            # Ausgabe CBC Crawler / Eingabe Tech Crawler
├── sscui_technical_info.xlsx    # Endergebnis
├── Configure Your Business      # Referenzliste für Vollständigkeitsprüfung
│   Processes(1).xlsx
└── DOKUMENTATION.md             # Diese Datei

C:\Users\goeth\desktop\SAP_Config_Bot\
└── .env                         # ANTHROPIC_API_KEY (wird automatisch gefunden)
```
