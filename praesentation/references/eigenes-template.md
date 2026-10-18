# Eigenes Theme anlegen

Ein Theme ist ein Ordner mit `theme.css` (Token) und `theme.json` (Schriften, Lockup,
Favicon). Die Engine bleibt gleich — Bausteine, Modi, Versand und PDF funktionieren
mit jedem Theme.

## 1. Ausgangspunkt kopieren

```
cp -r <skill>/assets/themes/neutral <skill>/assets/themes/<marke>
```

Gehört das Theme zu einem Kunden oder Partner und nicht ins Repo, den Ordner neben die
Präsentation legen und mit `--theme <pfad>` übergeben.

## 2. Vorgaben einsammeln

Vom Nutzer oder aus dem Styleguide der Marke: Grundfarbe/Papier, Textfarbe,
**eine** Akzentfarbe, Markierungsfarbe für Eyebrows, Hintergrund der Titelfolie,
Schriften (mit Lizenz für Einbettung), Logo (SVG bevorzugt). Fehlt etwas, fragen —
nicht raten. Eine Marke ohne dunkle Variante bekommt eine abgeleitete dunkle; das
in der README der Präsentation sagen.

## 3. Token setzen (`theme.css`)

Alle Token müssen **im hellen `:root`-Block** stehen; der Block
`:root[data-theme="dark"]` überschreibt nur, was sich im Dunkeln ändert.

| Token | Wofür |
|---|---|
| `--d-bg`, `--d-surface`, `--d-surface-sunk` | Grundfläche, Karten, vertiefte Flächen |
| `--d-ink`, `--d-ink-2`, `--d-ink-3`, `--d-ink-4` | Text: Haupt, Zweit (Lead), Dritt (Hinweise), Dekor |
| `--d-line`, `--d-line-strong` | Linien, Rahmen |
| `--d-accent` (+ `-strong`, `-mid`, `-soft`, `-pale`) | Akzent: Balken, Messwerte, Pfeile; Abstufungen für Linien und Flächen |
| `--d-mark` | Eyebrows und Nummern |
| `--d-ai`, `--d-ai-bg`, `--d-ai-line`, `--d-ai-text` | KI-Karte (eigene Farbfamilie, deutlich vom Akzent getrennt) |
| `--d-font-display`, `--d-font-text`, `--d-font-data` | Überschriften, Fließtext, Daten/Eyebrows (Monospace) |
| `--d-wm-weight` | Gewicht der Wortmarke außerhalb von `<b>` |
| `--d-radius-action`, `--d-radius-surface`, `--d-shadow`, `--d-dur` | Knöpfe, Flächen, Notizfeld, Hover-Dauer |
| `--d-brand-bg`, `--d-on-brand*` | Titel-/Schlussfolie und Bedienleiste darauf (Text, Zweittext, Eyebrow, Logo, Knopfrahmen, Hover, Hinweis, Fortschrittsbalken) |
| `--d-player-*` | Videoplayer — dunkle Insel in beiden Modi |

Die Deck-Maße (`--fs-*`, `--pad-*`) kommen aus der Engine; ein Theme darf sie
überschreiben, sollte es aber nur mit Grund tun.

## 4. `theme.json`

```json
{
  "name": "Marke",
  "beschreibung": "Herkunft der Werte (Styleguide, Version)",
  "schriften": [{"familie": "Inter", "gewicht": 400, "datei": "fonts/inter-400.woff2"}],
  "lockup": "<span class=\"lockup\"><svg viewBox=\"…\">…</svg><span class=\"wm\"><b>Marke</b></span></span>",
  "favicon": "<link rel=\"icon\" href=\"data:image/svg+xml,…\">",
  "titel_praefix": "Marke · ",
  "standard": false
}
```

- `standard`: `true` macht das Theme zum Vorgabewert von `neu.py` (höchstens eines).
- `schriften`: nur `.woff2`, Pfade relativ zum Theme-Ordner; Lizenzdatei (z. B. OFL)
  daneben legen. Leere Liste = Systemschriften (keine Einbettung, sieht je Rechner anders aus).
- `lockup`: Logo-SVG mit `fill="currentColor"`/`stroke="currentColor"`, damit es die
  Farbe der Umgebung übernimmt; `{{MARKE}}` wird durch `--marke` ersetzt.
- Ein Raster-Logo geht auch: `<img src="data:image/png;base64,…" alt="">` im Lockup.

## 5. Prüfen

```
python3 <skill>/scripts/kontrast.py <theme-ordner>
```

Muss ohne `FAIL` und ohne `??` durchlaufen (Text ≥ 4,5:1, Signet ≥ 3:1, beide Sets).
Danach eine Galerie erzeugen und mit `pruefen.js` + Screenshots ansehen:

```
python3 <skill>/scripts/neu.py <scratchpad>/test.html --theme <theme-ordner> --titel Test --galerie
```
