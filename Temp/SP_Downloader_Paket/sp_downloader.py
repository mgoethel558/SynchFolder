"""
SharePoint Excel-Downloader (eigenstaendiges Paket)
===================================================

Durchsucht einen SharePoint-Ordner rekursiv und laedt Excel-Dateien herunter --
rein ueber die SharePoint-REST-API, authentifiziert ueber eine einmalige
Browser-Anmeldung (die Session wird lokal im Ordner .pw-profile gespeichert).

Es werden KEINE Zugangsdaten gespeichert oder mitgeliefert -- jede Person meldet
sich mit dem eigenen Konto an und sieht nur, worauf sie ohnehin Zugriff hat.

Bedienung: ueblicherweise ueber START_HIER.bat (fragt alles interaktiv ab).
Direkter Aufruf ebenfalls moeglich:
    python sp_downloader.py "<ORDNER-URL>" [NAMENS-PRAEFIX]
"""
import os
import sys
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, parse_qs

from playwright.sync_api import sync_playwright

# --- Konfiguration -----------------------------------------------------------
BASE_DIR = Path(__file__).parent
# Download-Ziel bleibt im Paketordner (die Dateien soll der Nutzer sehen).
DEST_ROOT = BASE_DIR / "Downloads"
# Browser-Session (.pw-profile) hingegen in LOCALAPPDATA ablegen -- NICHT im
# Paketordner. Liegt das Paket in OneDrive/SharePoint-Sync, wuerde die
# Synchronisierung sonst die Datei-Locks der Browser-Session stoeren.
_APPDATA = Path(os.environ.get("LOCALAPPDATA", BASE_DIR)) / "SP-Downloader"
PROFILE_DIR = _APPDATA / ".pw-profile"
EXCEL_EXT = (".xlsx", ".xlsm", ".xlsb", ".xls")
# -----------------------------------------------------------------------------


def parse_url(arg: str):
    """Leitet (site_url, server_relativer_ordnerpfad) aus einer SharePoint-URL
    oder einem server-relativen Pfad ab. Funktioniert fuer beliebige Tenants
    und Sites -- nichts ist fest verdrahtet."""
    arg = arg.strip().strip('"').strip("'")

    if not arg.lower().startswith("http"):
        # Server-relativer Pfad wie /sites/<Site>/... -> Site = erste 2 Segmente
        path = arg
        host = None
    else:
        parsed = urlparse(arg)
        host = f"{parsed.scheme}://{parsed.netloc}"
        qs = parse_qs(parsed.query)
        if "id" in qs:                       # AllItems.aspx?id=<server-rel-pfad>
            path = unquote(qs["id"][0])
        else:
            path = unquote(parsed.path)
            # Freigabe-Links /:f:/r/sites/... oder /:x:/r/sites/... bereinigen
            for marker in ("/r/sites/", "/r/teams/"):
                i = path.find(marker)
                if i != -1:
                    path = path[i + 2:]       # "/r" abschneiden -> "/sites/..."
                    break

    # Site-relativen Teil bestimmen: /sites/<Name> oder /teams/<Name>
    m = re.match(r"(/(?:sites|teams)/[^/]+)", path, re.IGNORECASE)
    if not m:
        raise ValueError(
            "Konnte die Site nicht aus der URL ableiten. Erwartet wird ein Pfad "
            "mit /sites/<Name>/ oder /teams/<Name>/.\nEingabe war: " + arg)
    site_rel = m.group(1)

    if host is None:
        raise ValueError(
            "Bei server-relativem Pfad bitte die volle https-URL verwenden, "
            "damit der Server (z. B. https://firma.sharepoint.com) bekannt ist.")

    site_url = host + site_rel
    return site_url, path


def api_list(req, site_url: str, folder: str):
    """Listet (Unterordner, Dateien) eines Ordners via REST-API."""
    enc = quote(folder, safe="")
    base = f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{enc}')"
    headers = {"Accept": "application/json;odata=nometadata"}
    folders, files = [], []
    # SharePoint-System-/Infrastrukturordner, die beim Durchsuchen ab dem
    # Site-Root nicht relevant sind und uebersprungen werden.
    SYSTEM_FOLDERS = {
        "forms", "_catalogs", "_cts", "_private", "_vti_pvt",
        "style library", "sitepages", "siteassets", "formservertemplates",
        "images", "agentassets", "lists",
    }
    r = req.get(f"{base}/Folders", headers=headers)
    if r.ok:
        for f in json.loads(r.text()).get("value", []):
            if f.get("Name", "").lower() not in SYSTEM_FOLDERS:
                folders.append(f["ServerRelativeUrl"])
    r = req.get(f"{base}/Files", headers=headers)
    if r.ok:
        for f in json.loads(r.text()).get("value", []):
            files.append((f["Name"], f["ServerRelativeUrl"]))
    return folders, files


def walk(req, site_url: str, root: str, prefix: str = ""):
    """Rekursiv alle Excel-Dateien einsammeln (optional nach Praefix gefiltert)."""
    pfx = prefix.lower()
    found, stack = [], [root]
    while stack:
        cur = stack.pop()
        subfolders, files = api_list(req, site_url, cur)
        stack.extend(subfolders)
        for name, url in files:
            if not name.lower().endswith(EXCEL_EXT):
                continue
            if pfx and not name.lower().startswith(pfx):
                continue
            found.append((name, url))
            print(f"   gefunden: {name}")
    return found


def download(req, site_url: str, root: str, name: str, url: str) -> bool:
    """Laedt eine Datei via REST-API herunter und spiegelt die Ordnerstruktur."""
    rel = url[len(root):].lstrip("/") if url.startswith(root) else name
    dest = DEST_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    enc = quote(url, safe="")
    api_url = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{enc}')/$value"
    try:
        r = req.get(api_url, headers={"Accept": "application/octet-stream"})
        if not r.ok:
            print(f"   FEHLER bei {name}: HTTP {r.status}")
            return False
        dest.write_bytes(r.body())
        print(f"   OK -> {dest.relative_to(BASE_DIR)}")
        return True
    except Exception as e:
        print(f"   FEHLER bei {name}: {e}")
        return False


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def main() -> int:
    print("=" * 64)
    print(" SharePoint Excel-Downloader")
    print("=" * 64)

    folder_arg = sys.argv[1] if len(sys.argv) > 1 else ask(
        "\nOrdner-URL aus SharePoint einfuegen und Enter druecken:\n> ")
    if not folder_arg:
        print("!! Keine URL angegeben. Abbruch.")
        return 1

    prefix = sys.argv[2] if len(sys.argv) > 2 else ask(
        "Nur Dateien mit bestimmtem Namensanfang? (leer = alle Excel):\n> ")

    try:
        site_url, root = parse_url(folder_arg)
    except ValueError as e:
        print(f"!! {e}")
        return 1

    print(f"\n>> Site:        {site_url}")
    print(f">> Ordner:      {root}")
    print(f">> Filter:      {prefix!r}" if prefix else ">> Filter:      (alle Excel)")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            accept_downloads=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        host = urlparse(site_url).netloc
        print("\n>> Browser oeffnet sich. Bitte bei SharePoint anmelden "
              "(falls noch nicht angemeldet) ...")
        page.goto(site_url, wait_until="domcontentloaded")
        try:
            page.wait_for_url(lambda u: host in u, timeout=300_000)
        except Exception:
            print("!! Login-Timeout (5 Min). Bitte erneut starten.")
            ctx.close()
            return 1

        print(">> Angemeldet. Durchsuche Ordner rekursiv ...")
        files = walk(ctx.request, site_url, root, prefix)
        print(f"\n>> {len(files)} Excel-Datei(en) gefunden. Lade herunter (via API) ...")
        ok = sum(download(ctx.request, site_url, root, n, u) for n, u in files)
        ctx.close()

    print("\n" + "=" * 64)
    print(f" Fertig: {ok}/{len(files)} Datei(en) -> Ordner 'Downloads'")
    print("=" * 64)
    return 0 if ok == len(files) else 2


if __name__ == "__main__":
    code = main()
    try:
        input("\nEnter druecken zum Beenden ...")
    except EOFError:
        pass
    sys.exit(code)
