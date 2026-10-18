"""Legt eine neue Präsentation an: eine HTML-Datei mit Theme, eingebetteten Schriften,
Engine und Startfolien, dazu einen leeren Ordner media/ daneben.

Die erzeugte Datei ist danach die Quelle — Folien werden direkt in ihr bearbeitet.

Aufruf (nur Python-Standardbibliothek; unter Windows `py` statt `python3`):
  python3 neu.py <ziel.html> --theme neutral --marke "Firma" --titel "Q4-Review" --sprache en
  python3 neu.py <ziel.html> --titel "Kennenlernen" --galerie      (Standard-Theme, alle Bausteine)
  python3 neu.py <ziel.html> --theme <pfad/zu/eigenem-theme-ordner> --titel "…"
"""
import argparse
import base64
import html
import json
import pathlib
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

LABELS = {
    "de": {
        "L_THEME_ARIA": "Zwischen hellem und dunklem Modus wechseln", "L_DARK": "Dunkel",
        "L_NOTES_ARIA": "Sprechernotizen einblenden", "L_NOTES": "Notizen",
        "L_FS_ARIA": "Vollbild umschalten", "L_FS": "Vollbild",
        "L_PREV": "Vorherige Folie", "L_NEXT": "Nächste Folie",
        "L_HINT": "Pfeiltasten: blättern · T: hell/dunkel · N: Notizen · F: Vollbild",
        "L_NOTES_TITLE": "Sprechernotizen",
    },
    "en": {
        "L_THEME_ARIA": "Switch between light and dark mode", "L_DARK": "Dark",
        "L_NOTES_ARIA": "Show speaker notes", "L_NOTES": "Notes",
        "L_FS_ARIA": "Toggle full screen", "L_FS": "Full screen",
        "L_PREV": "Previous slide", "L_NEXT": "Next slide",
        "L_HINT": "Arrow keys: navigate · T: light/dark · N: notes · F: full screen",
        "L_NOTES_TITLE": "Speaker notes",
    },
}


def theme_ordner(name: str) -> pathlib.Path:
    eingebaut = ASSETS / "themes" / name
    pfad = eingebaut if eingebaut.is_dir() else pathlib.Path(name)
    if not (pfad / "theme.css").is_file() or not (pfad / "theme.json").is_file():
        sys.exit("Theme nicht gefunden (theme.css + theme.json erwartet): %s" % name)
    return pfad


def schriften(ordner: pathlib.Path, liste: list) -> str:
    zeilen = []
    for s in liste:
        datei = ordner / s["datei"]
        if not datei.is_file():
            sys.exit("Schriftdatei fehlt: %s" % datei)
        b64 = base64.b64encode(datei.read_bytes()).decode("ascii")
        zeilen.append('@font-face{font-family:"%s";src:url(data:font/woff2;base64,%s) format("woff2");'
                      "font-weight:%s;font-display:swap}" % (s["familie"], b64, s["gewicht"]))
    return "\n".join(zeilen) or "/* Systemschriften — nichts einzubetten */"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ziel", help="Pfad der neuen HTML-Datei")
    standard = next((t.name for t in sorted((ASSETS / "themes").iterdir())
                     if (t / "theme.json").is_file()
                     and json.loads((t / "theme.json").read_text(encoding="utf-8")).get("standard")), "neutral")
    ap.add_argument("--theme", default=standard, help="Name unter assets/themes/ oder Pfad zu einem Theme-Ordner "
                    "(Standard: %s)" % standard)
    ap.add_argument("--titel", required=True, help="Titel im Browser-Tab (ohne Markenpräfix)")
    ap.add_argument("--beschreibung", default="", help="meta description")
    ap.add_argument("--marke", default="", help="Wortmarke für Themes mit {{MARKE}} im Lockup (z. B. neutral)")
    ap.add_argument("--sprache", default="de", choices=sorted(LABELS))
    ap.add_argument("--galerie", action="store_true", help="alle Bausteine als Beispielfolien statt der drei Startfolien")
    ap.add_argument("--ueberschreiben", action="store_true")
    a = ap.parse_args()

    ziel = pathlib.Path(a.ziel).resolve()
    if ziel.exists() and not a.ueberschreiben:
        sys.exit("Existiert schon (--ueberschreiben, wenn gewollt): %s" % ziel)

    tord = theme_ordner(a.theme)
    theme = json.loads((tord / "theme.json").read_text(encoding="utf-8"))
    lockup = theme["lockup"]
    if "{{MARKE}}" in lockup:
        if not a.marke:
            sys.exit("Theme '%s' braucht --marke (Wortmarke im Lockup)" % theme["name"])
        lockup = lockup.replace("{{MARKE}}", html.escape(a.marke))

    folien = (ASSETS / "folien" / ("galerie.html" if a.galerie else "start.html")).read_text(encoding="utf-8")
    werte = {
        "SPRACHE": a.sprache,
        "TITEL": html.escape(theme.get("titel_praefix", "") + a.titel),
        "BESCHREIBUNG": html.escape(a.beschreibung),
        "FAVICON": theme.get("favicon", ""),
        "THEME": theme["name"],
        "SCHRIFTEN": schriften(tord, theme.get("schriften", [])),
        "THEME_CSS": (tord / "theme.css").read_text(encoding="utf-8").strip(),
        "ENGINE_CSS": (ASSETS / "engine.css").read_text(encoding="utf-8").strip(),
        "ENGINE_JS": (ASSETS / "engine.js").read_text(encoding="utf-8").strip(),
        "FOLIEN": folien.strip(),
        **LABELS[a.sprache],
    }
    text = (ASSETS / "geruest.html").read_text(encoding="utf-8")
    # FOLIEN zuletzt, damit {{LOCKUP}} in den Folien mit ersetzt wird
    for schluessel, wert in werte.items():
        text = text.replace("{{%s}}" % schluessel, wert)
    text = text.replace("{{LOCKUP}}", lockup)
    rest = sorted({t for t in text.split("{{")[1:] if "}}" in t[:40]})
    if rest:
        sys.exit("Unersetzte Platzhalter: %s" % ", ".join(r.split("}}")[0] for r in rest))

    ziel.parent.mkdir(parents=True, exist_ok=True)
    (ziel.parent / "media").mkdir(exist_ok=True)
    ziel.write_text(text, encoding="utf-8")
    print("angelegt: %s (%.0f KB, Theme %s, %s)" % (ziel, ziel.stat().st_size / 1024, theme["name"],
                                                 "Galerie" if a.galerie else "Startfolien"))


if __name__ == "__main__":
    main()
