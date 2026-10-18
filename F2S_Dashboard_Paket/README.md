# Fit-to-Standard Outcome Dashboard

Lokales HTML-Dashboard zur Auswertung der F2S-Workshop-Outcome-Dateien aus
SharePoint. Läuft vollständig offline; der einzige externe Zugriff ist das
**lesende** Herunterladen der Excel-Dateien aus SharePoint.

---

## 1. Schnellstart

Es gibt zwei Dateien:

- **`Dashboard.html`** — zum **Ansehen** (Doppelklick, öffnet im Browser, kein
  Server). Zeigt den zuletzt geladenen Stand, auch offline.
- **`Aktualisieren.bat`** — zum **Daten holen** aus SharePoint (Doppelklick):
  lädt die Excel-Dateien (lesend), wertet sie aus, schreibt die Historie und
  öffnet das Dashboard.

Voraussetzung: Python 3.10+ mit `openpyxl` und `playwright` (im
weitergabefähigen Paket bereits enthalten, siehe Abschnitt 5).

### Testmodus ohne SharePoint

Zum Testen mit lokalen Dateien statt SharePoint:

```
# aus dem Ordner F2S_Dashboard:
python app/refresh.py --source "PFAD/zu/einem/Ordner/mit/F2S-Dateien"
```

Danach `Dashboard.html` per Doppelklick öffnen.

> Hinweis: Ein optionaler localhost-Server (`app/backend.py` mit Live-Button)
> ist im Code weiterhin vorhanden, wird aber im Weitergabe-Paket nicht genutzt.

---

## 2. SharePoint konfigurieren

1. Im Ordner `app/` die Datei `config.local.json.example` nach
   `config.local.json` kopieren.
2. Die `folder_url` auf den SharePoint-Ordner setzen, in dem die
   `F2S_Workshop_Outcome_*.xlsx` liegen (Freigabe-Link oder normaler
   Ordner-Link).

Beim ersten „Aktualisieren" öffnet sich ein Browserfenster zur **einmaligen**
SharePoint-Anmeldung (inkl. MFA). Die Sitzung wird benutzerbezogen gespeichert
(`%LOCALAPPDATA%\F2S-Dashboard\.pw-profile`), sodass weitere Läufe ohne
erneutes Login auskommen.

---

## 3. Bedienung

- **Aktualisieren.bat**: lädt die Excel-Dateien (lesend), wertet sie aus, hängt
  einen Snapshot an die Historie an (`data/snapshots.json`), schreibt
  `data/snapshots.js` für die Anzeige und öffnet das Dashboard. Der temporäre
  Download-Ordner wird nach jedem Lauf geleert — auch bei Fehlern.
- **Dashboard.html**: zeigt den zuletzt geladenen Stand (Doppelklick).
- **PDF-Export**: öffnet den Druckdialog (A4 quer); „Als PDF speichern" wählen.
- **DE/EN** (oben rechts): schaltet alle Texte um; die Auswahl wird gemerkt.
- **Tabelle**: Spaltenüberschriften sortieren; LoB-Zeilen zum Aufklappen der
  Areas anklicken.

---

## 4. Ablageorte

| Ort | Inhalt |
|---|---|
| `data/snapshots.json` | Append-only Historie aller Läufe. Das Dashboard rendert immer hieraus — auch ohne Excel und nach Neustart. |
| `temp/` | Temporäre Excel-Downloads. Nach jedem Lauf leer. |
| `app/mapping.config.json` | Spalten- und Status-Zuordnung (siehe unten). |
| `app/config.local.json` | SharePoint-Ordner-URL (nicht mitgeliefert; lokal anzulegen). |
| `%LOCALAPPDATA%\F2S-Dashboard\` | Browser-Binaries + SharePoint-Login-Session (nicht im Projektordner, wegen OneDrive-Sync). |

---

## 5. Mapping anpassen (ohne Code-Änderung)

`app/mapping.config.json` steuert die Auswertung:

- **`summary_cells`** — welche Zelle im Sheet *Workshop Summary* welches Feld
  liefert (z. B. Workstream = `C8`).
- **`log_columns`** — welche Spalte im Sheet *Outcome Log* welches Feld ist
  (z. B. Record Type = `B`, Fit Assessment = `H`).
- **`count_rules`** — Decision/Task zählen nur, wenn das jeweilige Textfeld
  gefüllt ist.
- **`status_maps`** — Zuordnung der Excel-Statuswerte auf
  `offen / in Arbeit / erledigt`. Neue Werte hier ergänzen.
- Nicht zugeordnete Werte werden als **`unbekannt`** gezählt, als Warnung
  angezeigt und nie stillschweigend verworfen.

Nach Änderungen an der Config genügt ein erneutes „Aktualisieren" (bzw. ein
Neuladen der Seite, da die Config beim Rendern vom Backend gelesen wird).

---

## 6. Datenmodell (Kurzfassung)

- Eine Excel-Datei = ein Workshop (Sheet *Workshop Summary* + *Outcome Log*).
- **Workstream** = Line of Business (Primär-Gruppierung), **Area** = zweite Ebene.
- **Workshop „durchgeführt"**: sobald *Overall Result* gefüllt ist.
- **Requirement/Issue**-Status aus *Fit Assessment*;
  **Task**-Status aus *Action Status*; **Decision**-Status aus *Decision Status*.
- **Decision/Task** zählen nur bei gefülltem Textfeld (Decision bzw. Action).
- **Burn-up (Grafik A)** entsteht aus der Snapshot-Historie, da die Excel kein
  Erstell-/Abschlussdatum je Eintrag enthält.

Vollständige Beschreibung: `SPEZIFIKATION.md`.

---

## 7. Sicherheit

- Auf SharePoint wird **ausschließlich lesend** zugegriffen (REST-`GET`).
  Es wird dort nichts geschrieben, verschoben oder gelöscht.
- Keine Cloud-Dienste, keine externen CDNs, keine Telemetrie.
- Alle Ressourcen (Chart-Bibliothek, Skripte) liegen lokal.
