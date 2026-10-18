"""
SharePoint-Ordner rekursiv nach Excel-Dateien durchsuchen und herunterladen.

Nutzt die beim ersten Lauf von sp_download.py gespeicherte Session
(Temp/.pw-profile). Falls noch nicht eingeloggt, oeffnet sich ein Browser
zum einmaligen Anmelden.

Nutzung:
    python Temp/sp_download_folder.py "<ORDNER-URL ODER SERVER-RELATIVER PFAD>" [NAMENS-PRAEFIX]

    - Download laeuft rein ueber die SharePoint-REST-API (GetFileByServerRelativeUrl/$value),
      authentifiziert ueber die gespeicherte Browser-Session (Temp/.pw-profile).
    - Optionales 2. Argument: nur Dateien herunterladen, deren Name damit beginnt.
      Weglassen -> alle Excel-Dateien. Fuer "alle" explizit "" uebergeben.

Beispiele:
    # Nur Dateien, die mit F2S beginnen:
    python Temp/sp_download_folder.py "<ORDNER-URL>" F2S
    # Voller Browser-Link auf den Ordner:
    "https://lohgroup.sharepoint.com/sites/NameUnbekannt_ERPProgram/Shared%20Documents/Forms/AllItems.aspx?id=/sites/.../03_2-Explore"
    # Oder einfach der server-relative Pfad:
    "/sites/NameUnbekannt_ERPProgram/Shared Documents/Projekt Organisation/03_2-Explore"

Alle gefundenen Excel-Dateien landen unter Temp/SP_Download/<Ordnerstruktur>/.
"""
import sys
import json
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, parse_qs
from playwright.sync_api import sync_playwright

# --- Konfiguration -----------------------------------------------------------
SITE = "https://lohgroup.sharepoint.com/sites/NameUnbekannt_ERPProgram"
OUT_DIR = Path(__file__).parent
PROFILE_DIR = OUT_DIR / ".pw-profile"
DEST_ROOT = OUT_DIR / "SP_Download"
EXCEL_EXT = (".xlsx", ".xlsm", ".xlsb", ".xls")
# -----------------------------------------------------------------------------


def to_server_relative(arg: str) -> str:
    """Akzeptiert vollen Link ODER server-relativen Pfad und liefert den
    server-relativen Pfad (mit echten Leerzeichen) zurueck."""
    arg = arg.strip().strip('"').strip("'")
    if arg.lower().startswith("http"):
        parsed = urlparse(arg)
        qs = parse_qs(parsed.query)
        if "id" in qs:            # .../AllItems.aspx?id=<server-relativer-pfad>
            return unquote(qs["id"][0])
        path = unquote(parsed.path)
        # Freigabe-Links wie /:f:/r/sites/... oder /:x:/r/sites/... bereinigen:
        # fuehrenden ":x:/r"-Marker entfernen, sodass /sites/... uebrig bleibt.
        for marker in ("/r/sites/", "/r/teams/"):
            idx = path.find(marker)
            if idx != -1:
                return path[idx + 2:]  # schneidet "/r" ab -> "/sites/..."
        return path
    return arg


def api_list(req, server_relative_folder: str):
    """Listet (Unterordner, Dateien) eines Ordners via SharePoint REST-API."""
    enc = quote(server_relative_folder, safe="")
    base = f"{SITE}/_api/web/GetFolderByServerRelativeUrl('{enc}')"
    headers = {"Accept": "application/json;odata=nometadata"}

    folders, files = [], []
    r = req.get(f"{base}/Folders", headers=headers)
    if r.ok:
        for f in json.loads(r.text()).get("value", []):
            folders.append(f["ServerRelativeUrl"])
    r = req.get(f"{base}/Files", headers=headers)
    if r.ok:
        for f in json.loads(r.text()).get("value", []):
            files.append((f["Name"], f["ServerRelativeUrl"]))
    return folders, files


def walk(req, root: str, prefix: str = ""):
    """Rekursiv alle (Name, ServerRelativeUrl) der Excel-Dateien einsammeln.
    Optional nur Dateien, deren Name mit `prefix` beginnt (case-insensitive)."""
    pfx = prefix.lower()
    found, stack = [], [root]
    while stack:
        cur = stack.pop()
        subfolders, files = api_list(req, cur)
        stack.extend(subfolders)
        for name, url in files:
            if not name.lower().endswith(EXCEL_EXT):
                continue
            if pfx and not name.lower().startswith(pfx):
                continue
            found.append((name, url))
            print(f"   gefunden: {url}")
    return found


def download(req, root: str, name: str, server_relative_url: str) -> bool:
    """Laedt eine Datei rein ueber die REST-API (GetFileByServerRelativeUrl/$value)
    und spiegelt die Ordnerstruktur ab root. Nutzt die Session-Cookies des
    API-Request-Kontexts -- keine Browser-Navigation noetig."""
    rel = server_relative_url
    if rel.startswith(root):
        rel = rel[len(root):].lstrip("/")
    dest = DEST_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    enc = quote(server_relative_url, safe="")
    api_url = f"{SITE}/_api/web/GetFileByServerRelativeUrl('{enc}')/$value"
    try:
        r = req.get(api_url, headers={"Accept": "application/octet-stream"})
        if not r.ok:
            print(f"   FEHLER bei {name}: HTTP {r.status}")
            return False
        dest.write_bytes(r.body())
        print(f"   OK -> {dest}")
        return True
    except Exception as e:
        print(f"   FEHLER bei {name}: {e}")
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    root = to_server_relative(sys.argv[1])
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""
    print(f">> Zielordner (server-relativ): {root}")
    print(f">> Namens-Praefix-Filter: {prefix!r}" if prefix else ">> Kein Praefix-Filter (alle Excel)")

    PROFILE_DIR.mkdir(exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            accept_downloads=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(SITE, wait_until="domcontentloaded")
        try:
            page.wait_for_url(lambda u: "lohgroup.sharepoint.com" in u, timeout=300_000)
        except Exception:
            print("!! Login-Timeout."); ctx.close(); return 1

        print(">> Durchsuche Ordner rekursiv ...")
        files = walk(ctx.request, root, prefix)
        print(f">> {len(files)} Excel-Datei(en) gefunden. Starte Downloads (via API) ...")

        ok = sum(download(ctx.request, root, n, u) for n, u in files)
        print(f">> Fertig: {ok}/{len(files)} heruntergeladen -> {DEST_ROOT}")
        ctx.close()
        return 0 if ok == len(files) else 2


if __name__ == "__main__":
    sys.exit(main())
