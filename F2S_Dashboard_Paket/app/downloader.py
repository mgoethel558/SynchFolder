"""
downloader.py -- Duenner Wrapper um die vorhandene SharePoint-Download-Funktion.

Wiederverwendet die erprobte Logik aus sp_downloader.py (parse_url, walk,
REST-API, Playwright-Login) und laedt die F2S-Excel-Dateien LESEND in einen
uebergebenen Zielordner (hier: temp/). Auf SharePoint wird nichts veraendert.

Der Pfad zum Downloader-Paket wird automatisch gesucht; alternativ ueber die
Umgebungsvariable SP_DOWNLOADER_DIR gesetzt werden.
"""
from __future__ import annotations

import os
import sys
import importlib.util
from pathlib import Path
from urllib.parse import quote, urlparse


def _find_sp_downloader() -> Path:
    """Sucht sp_downloader.py in bekannten Orten."""
    env = os.environ.get("SP_DOWNLOADER_DIR")
    candidates = []
    if env:
        candidates.append(Path(env) / "sp_downloader.py")
    here = Path(__file__).resolve()
    # Im weitergabefaehigen Paket liegt sp_downloader.py neben app/ (oder in app/)
    candidates += [
        here.parent / "sp_downloader.py",
        here.parent.parent / "sp_downloader.py",
        # Entwicklungsort: Temp/SP_Downloader_Paket relativ zum Projekt
        here.parent.parent.parent / "Temp" / "SP_Downloader_Paket" / "sp_downloader.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "sp_downloader.py nicht gefunden. Bitte SP_DOWNLOADER_DIR setzen oder "
        "die Datei neben app/ ablegen. Gesucht:\n  " +
        "\n  ".join(str(c) for c in candidates))


def _load_module():
    path = _find_sp_downloader()
    spec = importlib.util.spec_from_file_location("sp_downloader", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sp_downloader"] = mod
    spec.loader.exec_module(mod)
    return mod


def download_f2s_files(folder_url: str, dest_dir: str | Path,
                       prefix: str = "F2S", log=print) -> list[Path]:
    """Laedt alle Excel-Dateien mit dem gegebenen Praefix aus dem SharePoint-
    Ordner LESEND nach dest_dir. Gibt die Liste der lokalen Pfade zurueck.

    Nutzt die persistente Playwright-Session (einmaliger Login noetig).
    """
    from playwright.sync_api import sync_playwright

    sp = _load_module()
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    site_url, root = sp.parse_url(folder_url)
    host_root = f"{urlparse(site_url).scheme}://{urlparse(site_url).netloc}"
    host = urlparse(site_url).netloc
    downloaded: list[Path] = []
    # Zuordnung Dateiname -> SharePoint-Web-URL (fuer Drill-down-Links).
    source_urls: dict[str, str] = {}

    sp.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(sp.PROFILE_DIR),
            headless=False,
            accept_downloads=True,
        )
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            log(">> Browser geoeffnet. Bitte ggf. bei SharePoint anmelden ...")
            page.goto(site_url, wait_until="domcontentloaded")
            page.wait_for_url(lambda u: host in u, timeout=300_000)
            log(">> Angemeldet. Durchsuche Ordner (nur lesend) ...")

            files = sp.walk(ctx.request, site_url, root, prefix)
            log(f">> {len(files)} Datei(en) gefunden. Lade herunter ...")

            for name, url in files:
                enc = quote(url, safe="")
                api_url = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{enc}')/$value"
                r = ctx.request.get(api_url, headers={"Accept": "application/octet-stream"})
                if not r.ok:
                    log(f"   FEHLER bei {name}: HTTP {r.status}")
                    continue
                target = dest_dir / name
                target.write_bytes(r.body())
                downloaded.append(target)
                # Web-URL der Datei (server-relative URL an den Host haengen).
                source_urls[name] = host_root + quote(url)
                log(f"   OK -> {name}")
        finally:
            ctx.close()

    download_f2s_files.last_source_urls = source_urls

    return downloaded
