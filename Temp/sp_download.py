"""
SharePoint-Download via Playwright (interaktiver Login, persistente Session).

Nutzung:
    python Temp/sp_download.py

Beim ersten Lauf oeffnet sich ein sichtbarer Browser. Melde dich normal bei
SharePoint an (inkl. MFA). Die Session wird im Ordner .pw-profile gespeichert,
sodass kuenftige Laeufe ohne erneutes Login funktionieren.
"""
import sys
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

# --- Konfiguration -----------------------------------------------------------
SITE = "https://lohgroup.sharepoint.com/sites/NameUnbekannt_ERPProgram"
# Server-relativer Pfad der Datei (Leerzeichen bleiben als echte Leerzeichen):
FILE_SERVER_RELATIVE = (
    "/sites/NameUnbekannt_ERPProgram/Shared Documents/"
    "Projekt Organisation/03_2-Explore/03_Workstreams/R2R_Finance/TEST_FI.xlsx"
)
OUT_DIR = Path(__file__).parent
PROFILE_DIR = OUT_DIR / ".pw-profile"
OUT_FILE = OUT_DIR / "TEST_FI.xlsx"
# -----------------------------------------------------------------------------

# download.aspx erzwingt den Datei-Download statt der Excel-Online-Ansicht.
download_url = f"{SITE}/_layouts/15/download.aspx?SourceUrl={quote(FILE_SERVER_RELATIVE)}"


def main() -> int:
    PROFILE_DIR.mkdir(exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            accept_downloads=True,
            # Eigenes Playwright-Chromium (vermeidet Konflikt mit bereits
            # geoeffnetem Edge/Chrome). Eigenes Profil -> einmaliger Login.
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print(">> Oeffne Login-Seite. Bitte im Browser bei SharePoint anmelden ...")
        page.goto(SITE, wait_until="domcontentloaded")

        # Warte, bis die Site erreichbar ist (nicht mehr auf login.microsoftonline.com)
        print(">> Warte auf erfolgreichen Login (bis zu 5 Minuten) ...")
        try:
            page.wait_for_url(lambda url: "lohgroup.sharepoint.com" in url, timeout=300_000)
        except Exception:
            print("!! Timeout beim Login. Bitte erneut versuchen.")
            ctx.close()
            return 1
        print(">> Login erkannt. Starte Download ...")

        try:
            with page.expect_download(timeout=120_000) as dl_info:
                # goto wirft "Download is starting", sobald die Navigation zum
                # Download wird -> erwartet, daher abfangen.
                try:
                    page.goto(download_url)
                except Exception:
                    pass
            download = dl_info.value
            download.save_as(str(OUT_FILE))
            print(f">> OK: gespeichert unter {OUT_FILE}")
            result = 0
        except Exception as e:
            print(f"!! Download fehlgeschlagen: {e}")
            print(f"   Versuchte URL: {download_url}")
            result = 2

        ctx.close()
        return result


if __name__ == "__main__":
    sys.exit(main())
