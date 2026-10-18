---
name: praesentation
description: >-
  Erstellt HTML-Präsentationen als eine einzige, offline lauffähige HTML-Datei mit
  Präsentationsmodus (Pfeiltasten, Klick, Wischen, Sprechernotizen, Hell/Dunkel, Vollbild),
  Lesemodus fürs Handy und Mail-Vorschau, dazu Versandfassung (alles eingebettet, ohne
  Notizen) und PDF (eine Folie pro Seite, Videos als Links) sowie eine automatische
  Prüfung auf Überlauf und Lesbarkeit. Gestaltung über austauschbare Themes: neutral
  oder ein eigenes Theme mit Farben, Schriften und Logo einer beliebigen Marke.
  Diesen Skill nutzen, wenn eine Präsentation, ein Deck, Folien, ein Vortrag,
  ein Pitch, eine Kennenlernpräsentation, Slides für einen Termin oder eine
  Versand-/PDF-Fassung davon verlangt wird — auch wenn der Nutzer „HTML“ nicht
  erwähnt. Nicht nutzen, wenn ausdrücklich eine .pptx- oder Google-Slides-Datei
  verlangt ist.
---

# HTML-Präsentation erstellen

`<skill>` steht unten für den Ordner dieses Skills (den Basisordner, aus dem diese
Datei geladen wurde, z. B. `.claude/skills/praesentation` im Projekt oder
`~/.claude/skills/praesentation` beim Nutzer). Alle Skripte finden ihre Vorlagen
relativ zu sich selbst — der Skill läuft in jedem Projekt.

## Was entsteht

| Fassung | Datei | Wofür |
|---|---|---|
| **Vortragsfassung** (Quelle) | `<name>.html` + `media/` daneben | Vortrag am Laptop/Beamer; mit Sprechernotizen (Taste N) |
| **Versandfassung HTML** | eine Datei, Bilder/Schriften/Untertitel eingebettet, Videos von öffentlicher Adresse | Mail, Laptop |
| **Versandfassung PDF** | 1920 × 1080 pro Folie, Videos und Links antippbar | WhatsApp, Handy (WhatsApp reicht HTML nicht an den Browser weiter) |

Alle Fassungen laufen in drei Modi: Präsentation (ab 900 × 560 px mit JS), Lesemodus
(darunter oder ohne JS — Folien untereinander) und PDF.

## Aufbau des Skills

```
assets/engine.css, engine.js      markenneutrale Engine (Modi, Navigation, Bausteine)
assets/geruest.html               Seitengerüst mit Platzhaltern
assets/themes/<name>/             je Theme: theme.css (Token), theme.json (Schriften, Logo)
assets/folien/start.html          drei Startfolien (Titel, Inhalt, Schluss)
assets/folien/galerie.html        jeder Baustein einmal
assets/README-vorlage.md          Gerüst für die README neben der Präsentation
scripts/neu.py                    legt eine neue Präsentation an
scripts/versand_bauen.py          Vortragsfassung → Versandfassung HTML
scripts/pdf_bauen.js              Versandfassung → PDF
scripts/pruefen.js                Überlauf, Bilder, Schriftgröße, Lesemodus — mit Screenshots
scripts/kontrast.py               WCAG-Prüfung eines Themes
scripts/package.json              Playwright für pruefen.js / pdf_bauen.js
scripts/export.py                 eigenständige Kopie des Skills erzeugen
references/bausteine.md           Katalog der Bausteine mit Regeln — vor dem Schreiben lesen
references/eigenes-template.md    neues Theme für eine Marke anlegen
```

Welche Themes vorhanden sind: `ls <skill>/assets/themes/`.

## Ablauf

### 1. Rahmen klären

Vor dem ersten Satz klären (aus dem Gespräch ableiten, nur Fehlendes fragen):

- **Anlass, Publikum, Dauer.** Faustregel: eine Folie pro Minute, 8–14 Folien.
- **Theme:** Gibt es eines für die Marke? Sonst `neutral` oder ein eigenes Theme nach
  `references/eigenes-template.md` (Farben, Schriften, Logo erfragen, nicht raten).
- **Material:** Fotos, Screenshots, Logos, Videos (mit öffentlicher Adresse?).
- **Ablage und Versand:** Wohin kommt die Quelle, braucht es HTML-/PDF-Versand, für wen?
- **Sprache:** `de` (Standard) oder `en` — betrifft Bedienleiste und Hinweise.

### 2. Storyline vor Gestaltung

Eine Folienliste schreiben: je Folie Eyebrow, Überschrift als **Aussage** (ganzer Satz),
Inhalt in Stichworten, Baustein aus `references/bausteine.md`, Inhalt der Sprechernotiz.
Bei mehr als einer Handvoll Folien oder unklarem Inhalt die Liste dem Nutzer zeigen und
das OK abwarten — umbauen ist in der Liste billig, im HTML teuer.

Bewährte Dramaturgie für Kennenlern- und Pilotpräsentationen: Titel → Wer wir sind →
Problem/Idee → Was es tut → Wie es funktioniert → Ablauf (Video) → Vertrauen/Datenschutz →
Ehrliche Grenzen → Was wir brauchen → Nächste Schritte + Fragen.

### 3. Gerüst anlegen

Python 3.9+, nur Standardbibliothek (`py` unter Windows, sonst `python3`):

```
python3 <skill>/scripts/neu.py <ordner>/<name>.html --theme neutral --marke "Firma" --titel "…" [--sprache en]
python3 <skill>/scripts/neu.py <ordner>/<name>.html --theme <theme-name | pfad/zum/theme-ordner> --titel "…"
```

`--galerie` statt der drei Startfolien alle Bausteine als Vorlage. Ohne `--theme` nimmt
das Skript das Theme mit `"standard": true` in seiner `theme.json`, sonst `neutral`. Es bettet die Schriften ein,
legt `media/` an und überschreibt nichts ohne `--ueberschreiben`. Die erzeugte Datei ist
ab jetzt die Quelle.

### 4. Folien schreiben

In der erzeugten Datei die Folien zwischen `<main id="deck">` und `</main>` ersetzen.
Bausteine und ihre Regeln: `references/bausteine.md`; lauffähige Beispiele in
`assets/folien/galerie.html`. Eigenes CSS nur in den Block „Folienspezifische
Ergänzungen“, Farben nur über `var(--d-*)`. Engine- und Theme-Block nicht anfassen.

Schreibregeln:
- Überschrift = Aussage der Folie, nicht Thema („Der Pilot ist kostenlos — und ehrlich
  begrenzt.“ statt „Pilot“).
- Höchstens vier Punkte, jeder ein ganzer Satz. Was gesagt, aber nicht gelesen werden
  soll, gehört in die Sprechernotiz.
- Keine erfundenen Zahlen, Zitate oder Logos. Beispielwerte als Beispiel kennzeichnen.
- Platzhalter für Fehlendes sichtbar lassen (`.placeholder` oder `[eckige Klammern]`)
  und dem Nutzer auflisten.

### 5. Bilder einbauen

Originale nach `media/`, bearbeitete Fassungen als `media/praes-*.jpg|png`, mit echten
`width`/`height` und sprechendem `alt`. Unbearbeitete Originale, die nicht weitergegeben
werden dürfen, in `media/.gitignore` eintragen. Personen, die nicht gezeigt werden
sollen, vor dem Einbau unkenntlich machen.

### 6. Prüfen — bis keine Befunde bleiben

Prüft beide Präsentationsgrößen (1366 × 768, 1920 × 1080) hell und dunkel, jede Folie,
plus Lesemodus mit und ohne JS. Exit-Code 1 bei Befunden.

```
node <skill>/scripts/pruefen.js <name>.html [--min-schrift 24] [--bilder <ordner>]
```

Danach **die Screenshots ansehen** (Read auf die PNGs) — der Prüfer findet Überlauf,
nicht schlechte Gestaltung. Mindestens Titel, je eine dichte Folie und den Lesemodus
anschauen. Bei Überlauf kürzen statt Schrift verkleinern.

### 7. Versandfassungen bauen

```
python3 <skill>/scripts/versand_bauen.py <name>.html <ziel>/<Versandname>.html [--video-basis https://…/videos/]
node <skill>/scripts/pdf_bauen.js <ziel>/<Versandname>.html <ziel>/<Versandname>.pdf
```

`versand_bauen.py` bricht ab, wenn noch ein `./media`-Verweis oder eine Notiz übrig
bleibt oder Videos ohne `--video-basis` eingebunden sind. Die Versandfassung danach
ebenfalls mit `pruefen.js` prüfen. Versandfassungen nie von Hand ändern — immer neu bauen.

### 8. README neben die Quelle

`assets/README-vorlage.md` neben die Präsentation kopieren und ausfüllen: Dateien,
Bedienung, welche Fassung wofür, Bau-Kommandos, offene Platzhalter, Bildnachweis mit
Bearbeitung, Videos, Abweichungen vom Designsystem mit Grund, „Geprüft am“ mit dem,
was tatsächlich geprüft wurde.

## Werkzeuge

`pruefen.js` und `pdf_bauen.js` brauchen Node 18+ und Playwright mit Chromium.

**Einmalig mit Node auf dem Rechner** (installiert in `<skill>/scripts/node_modules`,
von dort finden die Skripte das Paket selbst):

```
cd <skill>/scripts && npm install && npx playwright install chromium
```

**Ohne Node, mit Docker** (Git Bash unter Windows: `MSYS_NO_PATHCONV=1` voranstellen und
`$(pwd -W)` statt `$(pwd)`). Beim ersten Lauf legt `npm install` die `node_modules` im
Skill-Ordner an, danach entfällt der Schritt:

```
docker run --rm -v "<skill>:/skill" -v "$(pwd):/w" -w /w mcr.microsoft.com/playwright:v1.61.1-noble \
  sh -c "cd /skill/scripts && [ -d node_modules ] || npm install --no-audit --no-fund; cd /w && \
         node /skill/scripts/pruefen.js <pfad-relativ-zum-arbeitsordner>.html --bilder /w/<ordner>"
```

Die Image-Version muss zur Playwright-Version in `scripts/package.json` passen.

## Skill weitergeben

```
python3 <skill>/scripts/export.py <zielordner> [--zip]
```

Kopiert den Skill ohne `node_modules` und prüft die Kopie (Pflichtdateien,
Probelauf von `neu.py`). Den Zielordner nach `~/.claude/skills/praesentation/` (für alle
Projekte) oder `<projekt>/.claude/skills/praesentation/` legen.

## Bekannte Grenzen

- Untertitel (`<track>`) lädt Chrome in der **Vortragsfassung** über `file://` nicht
  (cross-origin); mit lokalem Webserver oder in der Versandfassung schon.
- Das neutrale Theme nutzt Systemschriften — Aussehen hängt vom Rechner ab. Für eine
  Marke immer Schriften einbetten.
- Neue Bausteine erst in einer Präsentation erproben, dann in `engine.css` +
  `galerie.html` + `bausteine.md` übernehmen.
