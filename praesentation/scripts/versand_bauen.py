"""Baut aus der Vortragsfassung die Versandfassung: eine einzige HTML-Datei.

- Bilder, Video-Vorschaubilder und Untertitel aus ./media werden eingebettet
- Videos kommen von einer öffentlichen Adresse (--video-basis), nie aus der Datei
- Sprechernotizen samt Knopf und Feld fallen weg (Regieanweisungen für die Vortragenden)
Die PDF-Fassung entsteht danach aus dieser Datei mit pdf_bauen.js.

Aufruf (nur Python-Standardbibliothek):
  python3 versand_bauen.py <vortrag.html> <versand.html> [--video-basis https://…/videos/]
"""
import argparse
import base64
import pathlib
import re
import sys

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
        ".gif": "image/gif", ".svg": "image/svg+xml"}
BILD = r"[\w .()-]+\.(?:jpe?g|png|webp|gif|svg)"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle")
    ap.add_argument("ziel")
    ap.add_argument("--video-basis", default="", help="öffentliche Adresse, unter der die .mp4 aus ./media liegen")
    a = ap.parse_args()

    quelle = pathlib.Path(a.quelle).resolve()
    media = quelle.parent / "media"
    html = quelle.read_text(encoding="utf-8")

    def data_uri(name: str) -> str:
        pfad = media / name
        if not pfad.is_file():
            sys.exit("Datei fehlt: %s" % pfad)
        return "data:%s;base64,%s" % (MIME[pfad.suffix.lower()], base64.b64encode(pfad.read_bytes()).decode("ascii"))

    # Sprechernotizen samt Knopf, Feld und Tastaturhinweis
    html, n_notes = re.subn(r"\s*<aside class=\"notes\">.*?</aside>", "", html, flags=re.S)
    html = re.sub(r"\s*<button class=\"cbtn\" id=\"notesBtn\".*?</button>", "", html, flags=re.S)
    html = re.sub(r"\s*<div class=\"notes-panel\".*?</div>\s*</div>", "", html, flags=re.S)
    html = re.sub(r" · N: [^·<]+?(?= ·|<)", "", html)

    # Bilder und Vorschaubilder einbetten
    html = re.sub(r'(src|poster)="\./media/(%s)"' % BILD, lambda m: '%s="%s"' % (m.group(1), data_uri(m.group(2))), html)

    # Videos von der öffentlichen Adresse
    videos = re.findall(r'<source src="\./media/([\w.-]+\.(?:mp4|webm))"', html)
    if videos and not a.video_basis:
        sys.exit("Videos in ./media (%s) — --video-basis angeben oder die Videos aus der Versandfassung nehmen"
                 % ", ".join(videos))
    basis = a.video_basis.rstrip("/") + "/"
    html = re.sub(r'<source src="\./media/([\w.-]+\.(?:mp4|webm))"', lambda m: '<source src="%s%s"' % (basis, m.group(1)), html)

    # Untertitel als <script type="text/vtt">; engine.js macht daraus eine Blob-Adresse
    vtt_bloecke = []

    def track(m: "re.Match[str]") -> str:
        name = m.group(1)
        inhalt = (media / (name + ".vtt")).read_text(encoding="utf-8")
        if "</script" in inhalt.lower():
            sys.exit("Untertitel enthalten </script: " + name)
        vtt_bloecke.append('<script type="text/vtt" id="vtt-%s">\n%s</script>' % (name, inhalt))
        return 'data-vtt="vtt-%s"' % name

    html = re.sub(r'src="\./media/([\w.-]+)\.vtt"', track, html)
    if vtt_bloecke:
        html = html.replace("</main>", "</main>\n\n" + "\n".join(vtt_bloecke), 1)

    # Nichts darf mehr auf die Nachbardateien zeigen, keine Notiz übrig bleiben
    rest = re.findall(r"\./media/[^\"' )]+", html)
    if rest:
        sys.exit("Noch Verweise auf ./media: %s" % ", ".join(sorted(set(rest))))
    if re.search(r'class="notes"|id="notesBtn"|class="notes-panel"', html):
        sys.exit("Sprechernotizen nicht vollständig entfernt")

    ziel = pathlib.Path(a.ziel).resolve()
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(html, encoding="utf-8")
    print("geschrieben: %s (%.1f MB; %d Notizen entfernt, %d Videos extern, %d Untertitel eingebettet)"
          % (ziel, ziel.stat().st_size / 1e6, n_notes, len(videos), len(vtt_bloecke)))


if __name__ == "__main__":
    main()
