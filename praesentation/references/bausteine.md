# Bausteine der Engine

Alle Bausteine stehen einmal lauffähig in `assets/folien/galerie.html`
(`neu.py … --galerie`). Diese Liste sagt, wofür jeder da ist und was dabei gilt.
Farben in eigenen Ergänzungen **nur** über `var(--d-*)` — dann folgen sie dem
Hell/Dunkel-Schalter und dem Theme.

## Folie

```html
<!-- 4 · Kurzname -->
<section class="slide">            <!-- slide--brand: Titel/Schluss in der zweiten Deckfarbe -->
  <p class="eyebrow">Thema</p>      <!-- Datenschrift, Versalien, Markenfarbe -->
  <h2>Die Überschrift ist die Aussage.</h2>
  …Inhalt…
  <aside class="notes">Sprechernotiz (Taste N; fällt in der Versandfassung weg)</aside>
</section>
```

- Der Kommentar `<!-- n · Kurzname -->` vor jeder Folie hält die Nummerierung lesbar.
- `h1` nur auf der Titelfolie, sonst `h2`.
- Jede Folie bekommt eine `aside.notes` — sie ist die Regieanweisung, nicht der Text der Folie.

## Text

| Klasse | Zweck | Regel |
|---|---|---|
| `.eyebrow` | Rubrik über der Überschrift | 1–4 Wörter |
| `h1` / `h2` | Aussage der Folie | ganzer Satz mit Punkt, max. ~12 Wörter |
| `.lead` | einordnender Absatz | max. 2 Sätze; bei Bedarf `style="max-width:60ch"` |
| `ul.points` | Aufzählung mit Balken | 2–4 Punkte, jeder ein Satz |
| `.claim` | Claim, Kontaktzeile | auf Titel/Schluss; Links mit `<a>` |
| `.card-sunk` | Beispiel/Hinweis vertieft | ein Absatz |

## Raster

| Klasse | Zweck |
|---|---|
| `.cols` | zwei gleiche Spalten; `.cols-wide-right` (5:6), `.cols-wide-left` (6:5) oder `style="grid-template-columns:7fr 5fr"` |
| `.stack` | Spalte mit gleichmäßigem Abstand (Karten untereinander) |
| `.slide-split` + `.split-main` + `figure.shot` | Text links, hohes Bild (Screenshot) rechts; Bildhöhe fest, Breite aus dem Seitenverhältnis |

Unter 760 px werden `.cols` und `.pair` einspaltig.

## Karten

| Klasse | Bedeutung | Erkennungszeichen |
|---|---|---|
| `.card` | neutrale Fläche | Linie 1 px; Titel als `p.eyebrow.card-title` |
| `.card.card-measured` + `.value` + `.value-sub` | **gemessener** Wert | gefüllter Punkt, Akzentfarbe, Datenschrift |
| `.card.card-ai` | **Deutung** durch KI | Raute als Kontur, eigene Farbfamilie, keine Ziffern |
| `.card.card-human` | Aussage eines Menschen | Text auf Grundfläche, Eyebrow aus Worten |
| `.pair` + `.match-word` | zwei `card-human` mit Vergleichswort dazwischen | „Gleich“ / „Verschieden“ — kein Urteil |

Gemessen und gedeutet stehen nie in derselben Karte.

## Personen, Bilder, Platzhalter

- `.card.person` mit `<img>` (quadratisch, 640 × 640) + `.person-name` + `.person-role`
- `figure.figure` mit `<img>` + `<figcaption>` — Unterschrift außerhalb des Bildes, kein Text im Bild
- `.placeholder` + `<span>BESCHRIFTUNG</span>` — gestreift, bis das echte Bild da ist
- Bilder immer mit `width`/`height` (echte Pixelmaße) und sprechendem `alt`
- Bilder liegen in `./media/`, bearbeitete Fassungen mit Präfix `praes-`

## Video

```html
<div class="player player-fill">       <!-- player-fill: füllt den Rest der Folie -->
  <div class="player-head"><span class="pt">Titel</span><span class="pm">Video · 2:11</span></div>
  <div class="player-stage">
    <video preload="none" controls poster="./media/name-poster.jpg">
      <source src="./media/name.mp4" type="video/mp4">
      <track kind="subtitles" srclang="de" label="Untertitel" src="./media/name.vtt" default>
    </video>
    <div class="start"><button type="button">Video abspielen</button></div>
    <a class="pdf-play" href="https://…/name.mp4"><span>Video ansehen</span></a>
  </div>
  <a class="video-link" href="https://…/name.mp4">Video im Browser öffnen: …/name.mp4</a>
</div>
```

- Ohne `player-fill` in einer Spalte; Höhe über `style="--video-max:58vh"`.
- `pdf-play` und `video-link` zeigen auf die **öffentliche** Adresse (dieselbe wie
  `--video-basis` von `versand_bauen.py`). Ohne öffentliche Adresse gehört das Video
  nicht in die Versandfassung.
- Untertitel lädt Chrome über `file://` in der Vortragsfassung nicht (cross-origin);
  in der Versandfassung schon (Blob-Adresse).

## Abläufe

- `.phases` (`style="--n:5"`) mit `.phase > .num + .nam + .des` — nummerierte Marken auf einer Linie
- `.steps` (`style="--n:4"`) mit `.step > .num + .nam + .des` — Schritte ohne Linie, auch auf `slide--brand`
- Nummern zweistellig: `01`, `02`, … Keine Icons — nummerierte Marken statt erfundener Zeichen.

## Diagramme

- Inline-SVG `class="diagram"`, `viewBox` ~1520 breit, Farben als `fill="var(--d-…)"`
- Text: `class="dt"` (Display), `class="dm"` (Datenschrift, Versalien), sonst Fließtextschrift;
  Schriftgröße im viewBox ≥ 22
- Breite Diagramme in `<div class="diagram-wrap">` + `<p class="swipe-hint">…</p>` danach
  (auf dem Handy seitlich wischbar)
- Kleine Skizze neben Text: `class="diagram diagram-small"`

## Titel und Co-Branding

```html
<div class="hero">{{LOCKUP}}</div>          <!-- neu.py setzt das Lockup des Themes ein -->

<!-- Co-Branding: Partner zuerst, Trennstrich, dann die eigene Marke -->
<div class="cobrand">
  <img class="crest" src="./media/praes-partner-logo.png" alt="Logo des Partners" width="…" height="…">
  <span class="cobrand-sep" aria-hidden="true"></span>
  …Lockup-HTML des Themes…
</div>
```

Partnerlogo unverändert (nicht beschneiden, nicht einfärben), nur die Fläche außerhalb
transparent machen; Höhe höchstens 1,3 × Signethöhe (ist in `.crest` eingestellt).

## Folienspezifisches CSS

Gehört in den Block „Folienspezifische Ergänzungen“ am Ende des `<style>`; kurze
Einzelwerte (`max-width`, `grid-template-columns`) dürfen inline stehen. Engine- und
Theme-Block in der Datei nicht ändern — sonst läuft die Präsentation von der Vorlage weg.
