"""Prüft die Farbpaare eines Themes gegen WCAG AA — helles und dunkles Set.

Liest die --d-*-Token aus theme.css (Hex-Werte direkt oder über var(--x) aufgelöst) und
rechnet die Paare nach, die die Engine tatsächlich verwendet.
Text ≥ 4,5:1, Nicht-Text (Linien, Punkte, Balken) ≥ 3:1.

Aufruf:  python3 kontrast.py <theme-ordner | theme.css>
"""
import pathlib
import re
import sys

# (Vordergrund, Hintergrund, Mindestwert, Bedeutung)
PAARE = [
    ("d-ink", "d-bg", 4.5, "Fließtext"),
    ("d-ink-2", "d-bg", 4.5, "Lead, Unterschriften"),
    ("d-ink-2", "d-surface", 4.5, "Text in Karten"),
    ("d-ink-2", "d-surface-sunk", 4.5, "Hinweiskarte"),
    ("d-ink-3", "d-bg", 4.5, "Tastaturhinweis"),
    ("d-mark", "d-bg", 4.5, "Eyebrow, Nummern"),
    ("d-mark", "d-surface", 4.5, "Eyebrow in Karten"),
    ("d-accent", "d-bg", 4.5, "Akzenttext, Messwert"),
    ("d-accent", "d-surface", 4.5, "Messwert in Karte"),
    ("d-ai", "d-ai-bg", 4.5, "KI-Eyebrow"),
    ("d-ai-text", "d-ai-bg", 4.5, "KI-Text"),
    ("d-on-brand", "d-brand-bg", 4.5, "Text auf Titelfolie"),
    ("d-on-brand-2", "d-brand-bg", 4.5, "Claim auf Titelfolie"),
    ("d-on-brand-mark", "d-brand-bg", 4.5, "Eyebrow auf Titelfolie"),
    ("d-on-brand-hint", "d-brand-bg", 4.5, "Hinweis auf Titelfolie"),
    ("d-on-brand-logo", "d-brand-bg", 3.0, "Signet auf Titelfolie"),
    ("d-player-ink", "d-player-bg", 4.5, "Videotitel"),
    ("d-player-meta", "d-player-bg", 4.5, "Videolänge"),
    ("d-player-btn-ink", "d-player-btn", 4.5, "Startknopf"),
    ("d-accent", "d-bg", 3.0, "Balken, Punkte, Pfeile"),
    ("d-accent-soft", "d-bg", 1.0, "Phasenlinie (dekorativ, nur Anzeige)"),
    ("d-line-strong", "d-bg", 1.0, "Rahmen (dekorativ, nur Anzeige)"),
]


def bloecke(css: str) -> tuple:
    hell, dunkel = {}, {}
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        ziel = dunkel if 'data-theme="dark"' in sel else hell if sel.strip() == ":root" else None
        if ziel is None:
            continue
        for k, v in re.findall(r"--([\w-]+)\s*:\s*([^;]+);", body):
            ziel[k] = v.strip()
    return hell, {**hell, **dunkel}


def aufloesen(tok: dict, name: str, tiefe: int = 0) -> str:
    v = tok.get(name, "")
    m = re.fullmatch(r"var\(--([\w-]+)\)", v)
    if m and tiefe < 10:
        return aufloesen(tok, m.group(1), tiefe + 1)
    return v


def lum(hexwert: str) -> float:
    h = hexwert.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def kontrast(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = pathlib.Path(sys.argv[1])
    css = (p / "theme.css" if p.is_dir() else p).read_text(encoding="utf-8")
    fehler = 0
    for setname, tok in zip(("hell", "dunkel"), bloecke(css)):
        print("== %s ==" % setname)
        for fg, bg, minimum, was in PAARE:
            a, b = aufloesen(tok, fg), aufloesen(tok, bg)
            if not (re.fullmatch(r"#[0-9a-fA-F]{3,6}", a) and re.fullmatch(r"#[0-9a-fA-F]{3,6}", b)):
                print("  ??    %-18s auf %-14s nicht auflösbar (%s / %s)" % (fg, bg, a or "fehlt", b or "fehlt"))
                fehler += 1
                continue
            k = kontrast(a, b)
            ok = k >= minimum
            fehler += not ok
            print("  %s %5.2f  %-18s auf %-14s %s (min %.1f)" % ("ok  " if ok else "FAIL", k, fg, bg, was, minimum))
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
