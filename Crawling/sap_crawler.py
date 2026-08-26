#!/usr/bin/env python3
"""
SAP ME Process Navigator Crawler
Crawlt Seiteninhalte nach automatischem Login mit parametrisierbaren URLs.
"""

import asyncio
import argparse
import getpass
import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill
from playwright.async_api import async_playwright, Page

URL_TEMPLATE = "https://me.sap.com/processnavigator/SolS/EARL_SolS-013/2602/SolP/{param}?region=DE"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def do_login(page: Page, username: str, password: str) -> bool:
    """Automatischer Login. Gibt True zurück wenn erfolgreich."""
    print("  Suche Login-Formular...")
    try:
        await page.wait_for_selector('input[type="password"]', timeout=10000)
    except Exception:
        return False

    for selector in [
        'input[type="email"]',
        'input[name="logonuidfield"]',
        'input[name="j_username"]',
        'input[name="username"]',
        'input[name="email"]',
        'input[id*="user" i]',
        'input[id*="email" i]',
    ]:
        try:
            await page.fill(selector, username)
            print(f"  Username eingegeben ({selector})")
            break
        except Exception:
            continue

    try:
        await page.fill('input[type="password"]', password)
        print("  Passwort eingegeben.")
    except Exception:
        print("  FEHLER: Passwort-Feld nicht befüllbar.")
        return False

    for selector in [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Log On")',
        'button:has-text("Login")',
        'button:has-text("Anmelden")',
        'button:has-text("Sign In")',
    ]:
        try:
            await page.click(selector)
            print(f"  Login-Button geklickt ({selector})")
            break
        except Exception:
            continue

    await page.wait_for_load_state("networkidle", timeout=20000)
    return True


async def manual_login_wait(page: Page):
    """Wartet auf manuellen Login durch den Nutzer."""
    print("\n" + "=" * 60)
    print("MANUELLER LOGIN MODUS")
    print("Bitte im Browserfenster einloggen.")
    print("Drücke ENTER sobald du eingeloggt bist...")
    print("=" * 60)
    input()


# ---------------------------------------------------------------------------
# iFrame-Helper
# ---------------------------------------------------------------------------

async def wait_for_sap_frame(page: Page, timeout_s: int = 60):
    """Wartet bis das <iframe> im DOM erscheint und Inhalt enthält."""

    # Schritt 1: warten bis iframe-Element im DOM sichtbar ist
    print("  Warte auf <iframe> Element im DOM...")
    try:
        await page.wait_for_selector(
            'iframe[src*="pr.alm.me.sap.com"]', timeout=timeout_s * 1000
        )
        print("  <iframe> Element gefunden.")
    except Exception:
        print("  WARNUNG: <iframe src='pr.alm...'> nicht im DOM – prüfe alle Frames.")

    # Schritt 2: Frame-Objekt mit Inhalt holen
    for attempt in range(timeout_s // 2):
        all_urls = [f.url[:70] for f in page.frames]
        print(f"  Frames ({len(page.frames)}): {all_urls}")

        for frame in page.frames:
            if "pr.alm.me.sap.com" in frame.url:
                try:
                    has = await frame.evaluate(
                        "() => !!document.body && document.body.innerText.trim().length > 200"
                    )
                    if has:
                        print(f"  iFrame mit Inhalt: {frame.url[:70]}")
                        return frame
                    print(f"  pr.alm Frame leer (Versuch {attempt+1})")
                except Exception as e:
                    print(f"  pr.alm Frame Fehler: {e}")
                break
        await asyncio.sleep(2)

    return None


# ---------------------------------------------------------------------------
# Element-Erkennung
# ---------------------------------------------------------------------------

async def get_page_elements(frame) -> list:
    """Extrahiert wählbare Elemente aus dem SAP-iFrame."""
    elements = await frame.evaluate("""
        () => {
            const results = [];
            let idx = 0;

            function preview(el, n = 80) {
                return el.innerText.trim().replace(/\\s+/g, ' ').slice(0, n);
            }

            // Bekannte SAP Process Navigator Regionen (aus Accessibility-Tree)
            const regionLabels = [
                'Beschreibung',
                'Diagramme',
                'Verwendet in',
                'Beschleuniger',
                'Lösungskomponente und Lizenzierung',
                'Relevanz Land/Region',
                'Relevanz Branche',
                'Lösungsfunktionen',
                'Neuerungen',
            ];
            for (const label of regionLabels) {
                const el = document.querySelector(
                    `[role="region"][aria-label*="${label}"], [aria-label*="${label}"]`
                );
                if (el && el.innerText.trim().length > 30) {
                    results.push({
                        idx: idx++, type: 'region',
                        label: `Region: ${label} → "${preview(el)}"`,
                        aria_label: label
                    });
                }
            }

            // Tabellen im Frame
            document.querySelectorAll('table').forEach((table, i) => {
                const headers = Array.from(table.querySelectorAll('th'))
                    .map(th => th.innerText.trim()).filter(t => t).slice(0, 5).join(', ');
                const rowCount = table.querySelectorAll('tr').length;
                if (rowCount > 1) {
                    results.push({
                        idx: idx++, type: 'table',
                        label: `Tabelle #${i+1} (${rowCount} Zeilen${headers ? ', Spalten: ' + headers : ''})`,
                        selector: `table:nth-of-type(${i+1})`
                    });
                }
            });

            // Fallback: Objektdetails-Hauptbereich
            const main = document.querySelector('[role="main"][aria-label*="Objektdetails"], [role="main"]');
            if (main && main.innerText.trim().length > 100) {
                results.push({
                    idx: idx++, type: 'region',
                    label: `Gesamter Objektdetail-Bereich → "${preview(main)}"`,
                    aria_label: null,
                    selector: '[role="main"]'
                });
            }

            return results;
        }
    """)
    return elements


async def extract_element(frame, element: dict):
    """Extrahiert Inhalt eines Elements aus dem SAP-iFrame."""
    el_type = element['type']

    if el_type == 'table':
        selector = element['selector']
        return await frame.evaluate(f"""
            () => {{
                const table = document.querySelector('{selector}');
                if (!table) return [];
                return Array.from(table.querySelectorAll('tr')).map(tr =>
                    Array.from(tr.querySelectorAll('th, td')).map(c => c.innerText.trim())
                );
            }}
        """)

    if el_type in ('region', 'labelledby'):
        selector = element.get('selector')
        return await frame.evaluate(f"""
            () => {{
                const el = document.querySelector("{selector}");
                return el ? el.innerText.trim() : '';
            }}
        """)

    return ''


# ---------------------------------------------------------------------------
# Text-Parser: Beschreibung in Untersektionen aufteilen
# ---------------------------------------------------------------------------

SECTION_MARKERS = [
    "Überblick",
    "Wichtiger Prozessablauf",
    "Geschäftlicher Nutzen",
]

def parse_beschreibung(text: str) -> dict:
    """Teilt den Beschreibungs-Text an bekannten Überschriften auf."""
    # Positionen der Marker suchen
    positions = []
    for marker in SECTION_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            positions.append((marker, idx))

    positions.sort(key=lambda x: x[1])

    sections = {m: "" for m in SECTION_MARKERS}
    for i, (marker, pos) in enumerate(positions):
        start = pos + len(marker)
        end   = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        sections[marker] = text[start:end].strip()

    return sections


# ---------------------------------------------------------------------------
# Excel-Ausgabe
# ---------------------------------------------------------------------------

COLUMNS = {
    "A": "Prozess-ID",
    "B": "Überblick",
    "C": "Wichtiger Prozessablauf",
    "D": "Geschäftlicher Nutzen",
    "E": "Lösungskomponente und Lizenzierung",
}

SHEET_NAME = "Ergebnisse"

def write_row(output_path: Path, param: str, beschreibung: str, loesungskomp: str):
    """Hängt eine neue Zeile an das gemeinsame Sheet an (eine Zeile pro Parameter)."""
    from openpyxl.styles import Alignment

    if output_path.exists():
        wb = load_workbook(output_path)
    else:
        wb = Workbook()
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']

    if SHEET_NAME not in wb.sheetnames:
        ws = wb.create_sheet(SHEET_NAME)
        # Header-Zeile beim ersten Anlegen schreiben
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
        for col_idx, (_, label) in enumerate(COLUMNS.items(), start=1):
            cell = ws.cell(row=1, column=col_idx, value=label)
            cell.font  = header_font
            cell.fill  = header_fill
    else:
        ws = wb[SHEET_NAME]

    # Nächste freie Zeile ermitteln
    next_row = ws.max_row + 1

    parsed = parse_beschreibung(beschreibung)

    ws.cell(row=next_row, column=1, value=param)
    ws.cell(row=next_row, column=2, value=parsed.get("Überblick", ""))
    ws.cell(row=next_row, column=3, value=parsed.get("Wichtiger Prozessablauf", ""))
    ws.cell(row=next_row, column=4, value=parsed.get("Geschäftlicher Nutzen", ""))
    ws.cell(row=next_row, column=5, value=loesungskomp)

    for col in range(1, 6):
        ws.cell(row=next_row, column=col).alignment = Alignment(wrap_text=True, vertical="top")

    ws.column_dimensions["A"].width = 15
    for letter in ["B", "C", "D", "E"]:
        ws.column_dimensions[letter].width = 80

    wb.save(output_path)


# ---------------------------------------------------------------------------
# Navigation Helper (SPA-sicher)
# ---------------------------------------------------------------------------

async def safe_goto(page: Page, url: str):
    """Navigiert zu einer URL und wartet bis das SPA-Routing zur Ziel-URL abgeschlossen ist."""
    try:
        await page.goto(url, wait_until="commit", timeout=30000)
    except Exception:
        pass
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass

    # SPA-Routing abwarten: prüfen ob wir auf der richtigen URL gelandet sind
    from urllib.parse import urlparse
    expected_path = urlparse(url).path
    for _ in range(10):
        if expected_path in page.url:
            break
        await asyncio.sleep(1)

    # Falls immer noch falsche URL: nochmal direkt navigieren
    if expected_path not in page.url:
        print(f"  SPA-Redirect erkannt ({page.url[:60]}...), navigiere erneut...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

    await asyncio.sleep(5)


# ---------------------------------------------------------------------------
# Haupt-Crawl-Logik
# ---------------------------------------------------------------------------

async def run_crawler(username: str, password: str, input_excel: Path,
                      output_excel: Path, manual: bool):

    # Parameter aus Excel lesen
    df = pd.read_excel(input_excel, header=None)
    params = [str(v).strip() for v in df.iloc[:, 0].dropna() if str(v).strip()]

    if not params:
        print("FEHLER: Keine Parameter in Spalte A gefunden.")
        return

    print(f"\n{len(params)} Parameter gefunden: {', '.join(params)}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page    = await context.new_page()

        first_url = URL_TEMPLATE.format(param=params[0])
        print(f"\nNavigiere zu: {first_url}")
        await safe_goto(page, first_url)

        # Login-Erkennung: Passwort-Feld ODER Weiterleitung auf fremde Domain
        current_url   = page.url
        on_login_page = (
            await page.query_selector('input[type="password"]') is not None
            or "accounts.sap.com" in current_url
            or "me.sap.com" not in current_url
        )

        if manual:
            # Im manuellen Modus IMMER warten – egal ob Login erkannt oder nicht
            print(f"\nAktuelle URL: {current_url}")
            await manual_login_wait(page)
            print(f"\nNavigiere nach Login zu: {first_url}")
            await safe_goto(page, first_url)
        elif on_login_page:
            print("\nLogin-Seite erkannt. Starte automatischen Login...")
            ok = await do_login(page, username, password)
            if not ok:
                print("Automatischer Login fehlgeschlagen → manueller Modus.")
                await manual_login_wait(page)
            print(f"\nNavigiere nach Login zu: {first_url}")
            await safe_goto(page, first_url)
        else:
            print("Bereits eingeloggt.")

        # Feste Extraktionsziele – Selektoren aus DOM-Analyse
        targets = [
            {"type": "labelledby", "label": "Beschreibung",
             "selector": "[aria-labelledby*='subsection_documentation']"},
            {"type": "labelledby", "label": "Lösungskomponente und Lizenzierung",
             "selector": "[aria-labelledby*='subsection_solutionComponent']"},
        ]

        # --- Crawling aller Parameter ---
        print("\n" + "=" * 60)
        print("STARTE CRAWLING")
        print("=" * 60)

        for i, param in enumerate(params, 1):
            url = URL_TEMPLATE.format(param=param)
            print(f"\n[{i}/{len(params)}] {url}")
            await safe_goto(page, url)

            frame = await wait_for_sap_frame(page, timeout_s=30)
            if not frame:
                print(f"  WARNUNG: iFrame für '{param}' nicht gefunden, überspringe.")
                continue

            beschreibung = await extract_element(frame, targets[0])
            loesungskomp = await extract_element(frame, targets[1])

            preview_b = (beschreibung or "")[:70].replace("\n", " ")
            preview_l = (loesungskomp  or "")[:70].replace("\n", " ")
            print(f"  ✓ Beschreibung:              {preview_b}")
            print(f"  ✓ Lösungskomponente:         {preview_l}")

            write_row(output_excel, param, beschreibung or "", loesungskomp or "")
            print(f"  → Zeile '{param}' gespeichert.")

        print(f"\n{'='*60}")
        print(f"FERTIG! Ausgabe: {output_excel.resolve()}")
        print(f"{'='*60}")

        await browser.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SAP ME Process Navigator Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Passwort wird sicher abgefragt (empfohlen):
  python sap_crawler.py -i parameter.xlsx -o ergebnisse.xlsx -u max@firma.com

  # Passwort direkt mitgeben:
  python sap_crawler.py -i parameter.xlsx -o ergebnisse.xlsx -u max@firma.com -p MeinPasswort

  # Manueller Login (du loggst dich selbst im Browser ein):
  python sap_crawler.py -i parameter.xlsx -o ergebnisse.xlsx -u max@firma.com --manual
        """,
    )

    parser.add_argument("--input",  "-i", required=True,
                        help="Excel-Datei mit Parametern in Spalte A")
    parser.add_argument("--output", "-o", required=True,
                        help="Ausgabe-Excel-Datei (wird erstellt oder ergänzt)")
    parser.add_argument("--user",   "-u", required=True,
                        help="SAP-Benutzername oder E-Mail-Adresse")
    parser.add_argument("--password", "-p", default=None,
                        help="Passwort (optional; wird sonst sicher abgefragt)")
    parser.add_argument("--manual", "-m", action="store_true",
                        help="Manueller Login: Browser öffnet sich, du loggst dich selbst ein")

    args = parser.parse_args()

    password = args.password
    if not password and not args.manual:
        password = getpass.getpass(f"Passwort für {args.user}: ")

    input_path  = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"FEHLER: Datei nicht gefunden: {input_path}")
        sys.exit(1)

    asyncio.run(run_crawler(
        username=args.user,
        password=password or "",
        input_excel=input_path,
        output_excel=output_path,
        manual=args.manual,
    ))


if __name__ == "__main__":
    main()
