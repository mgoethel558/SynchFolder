"""Erzeugt eine eigenständige Kopie des Skills, die in jedem Projekt läuft.

- kopiert alles außer node_modules, __pycache__ und Prüfausgaben
- prüft die Kopie: Pflichtdateien, Probelauf von neu.py

Aufruf (nur Python-Standardbibliothek; unter Windows `py` statt `python3`):
  python3 export.py <zielordner> [--zip]
Danach den Zielordner nach ~/.claude/skills/praesentation/ oder
<projekt>/.claude/skills/praesentation/ legen.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

SKILL = pathlib.Path(__file__).resolve().parent.parent
AUSLASSEN = {"node_modules", "__pycache__", ".pytest_cache"}
PFLICHT = ["SKILL.md", "assets/engine.css", "assets/engine.js", "assets/geruest.html",
           "assets/folien/start.html", "assets/folien/galerie.html", "assets/README-vorlage.md",
           "assets/themes/neutral/theme.css", "assets/themes/neutral/theme.json",
           "scripts/neu.py", "scripts/versand_bauen.py", "scripts/pdf_bauen.js", "scripts/pruefen.js",
           "scripts/kontrast.py", "scripts/package.json", "scripts/export.py",
           "references/bausteine.md", "references/eigenes-template.md"]
TEXT = {".md", ".py", ".js", ".css", ".html", ".json", ".txt"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ziel")
    ap.add_argument("--zip", action="store_true", help="zusätzlich <ziel>.zip anlegen")
    a = ap.parse_args()

    ziel = pathlib.Path(a.ziel).resolve()
    if ziel == SKILL or SKILL in ziel.parents:
        sys.exit("Ziel darf nicht im Skill-Ordner liegen: %s" % ziel)
    if ziel.exists() and any(ziel.iterdir()):
        sys.exit("Ziel existiert und ist nicht leer: %s" % ziel)

    def ignorieren(ordner: str, namen: list) -> set:
        weg = {n for n in namen if n in AUSLASSEN or n.endswith(".pyc")}
        return weg

    shutil.copytree(SKILL, ziel, ignore=ignorieren, dirs_exist_ok=True)

    fehlt = [p for p in PFLICHT if not (ziel / p).is_file()]
    if fehlt:
        sys.exit("Kopie unvollständig: %s" % ", ".join(fehlt))
    befunde = []
    with tempfile.TemporaryDirectory() as tmp:
        probe = subprocess.run([sys.executable, str(ziel / "scripts" / "neu.py"), str(pathlib.Path(tmp) / "probe.html"),
                                "--theme", "neutral", "--marke", "Probe", "--titel", "Probe", "--galerie"],
                               capture_output=True, text=True, encoding="utf-8")
        if probe.returncode != 0:
            befunde.append("Probelauf neu.py: %s" % (probe.stderr or probe.stdout).strip())
    if befunde:
        print("Befunde in der Kopie (%s):" % ziel)
        for b in befunde:
            print("  - " + b)
        sys.exit(1)

    themes = sorted(p.name for p in (ziel / "assets" / "themes").iterdir() if p.is_dir())
    print("exportiert: %s (Themes: %s)" % (ziel, ", ".join(themes)))
    if a.zip:
        archiv = shutil.make_archive(str(ziel), "zip", root_dir=ziel.parent, base_dir=ziel.name)
        print("Archiv: %s" % archiv)
    print("Einrichten: Ordner nach ~/.claude/skills/%s/ kopieren; für pruefen.js/pdf_bauen.js einmal\n"
          "  cd <skill>/scripts && npm install && npx playwright install chromium" % ziel.name)


if __name__ == "__main__":
    main()
