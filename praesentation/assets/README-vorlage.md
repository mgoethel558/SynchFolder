# [Titel der Präsentation]

HTML-Präsentation für **[Anlass] mit [Publikum]** ([Dauer] Minuten, [n] Folien).
Erstellt am [Datum] mit dem Skill `praesentation`, Theme `[theme]`.

## Dateien

| Datei / Ordner | Inhalt |
|---|---|
| `[name].html` | **Vortragsfassung** und Quelle: CSS, JS und Schriften in einer Datei, offline lauffähig; Bilder und Videos aus `media/` daneben |
| `[ziel]/[Versandname].html` | **Versandfassung als HTML**, erzeugt von `versand_bauen.py` — für Mail und Laptop. Nicht von Hand ändern |
| `[ziel]/[Versandname].pdf` | **Versandfassung als PDF**, erzeugt von `pdf_bauen.js` — für WhatsApp/Handy. Nicht von Hand ändern |
| `media/praes-*` | bearbeitete Bilder, die die Präsentation einbindet (siehe „Bilder“) |
| `media/[original]` | unbearbeitete Originale — **nicht weitergeben**, in `media/.gitignore` |

Öffnen per Doppelklick genügt. Untertitel lädt Chrome in der Vortragsfassung über
`file://` nicht; in der Versandfassung schon.

## Bedienung

- **Pfeiltasten / Bild auf/ab / Leertaste** blättern, **Pos1/Ende** springen
- **Klick** rechts = weiter, linkes Drittel = zurück; **Wischen** auf Touch-Geräten
- **T** hell/dunkel · **N** Sprechernotizen · **F** Vollbild
- Unter 900 × 560 px und ohne JavaScript: alle Folien untereinander (Lesemodus)

## Versenden

- **WhatsApp, Handy → PDF.** Videos und Links sind antippbar.
- **Mail, Laptop → HTML.** Im Browser öffnen, nicht in der Mail-Vorschau.
- Beide ohne Sprechernotizen. Videos laden von: [öffentliche Adresse]

## Bauen

Nach jeder Änderung an der Quelle oder den Bildern beide Fassungen neu bauen:

```
python3 <skill>/scripts/versand_bauen.py [name].html [ziel]/[Versandname].html --video-basis [adresse]
node <skill>/scripts/pdf_bauen.js [ziel]/[Versandname].html [ziel]/[Versandname].pdf
node <skill>/scripts/pruefen.js [ziel]/[Versandname].html
```

## Offene Platzhalter

- [Folie n: was fehlt] — oder „Keine mehr offen“

## Bilder

| Folie | Datei | Herkunft und Bearbeitung |
|---|---|---|
| [n · Name] | `praes-….jpg` | [Quelle; was verändert wurde: Zuschnitt, Verpixelung, Freistellung] |

## Videos

| Folie | Video | Warum dort |
|---|---|---|
| [n · Name] | `….mp4` ([Länge]) | [Begründung] |

## Gestaltung

Theme `[theme]`. Abweichungen vom Designsystem, jeweils mit Grund:

- [Abweichung — Grund]

## Geprüft am [Datum]

[Was tatsächlich geprüft wurde: pruefen.js ohne Befunde (Größen, hell/dunkel,
Lesemodus), Screenshots gesichtet, PDF-Seiten und Links, Kontrast.]
