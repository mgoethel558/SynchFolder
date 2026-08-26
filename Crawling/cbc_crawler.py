#!/usr/bin/env python3
"""
CBC SSCUI Crawler
Crawlt SSCUI Namen, Nummern und Links aus dem Configuration-Tab der CBC.
"""

import asyncio
import argparse
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from playwright.async_api import async_playwright, Page

CBC_URL     = "https://my56243466.prod02.cbc.eu.one.cloud.sap/sap/public/x4/bc/pe/index.html#/configuration_activities"
SHEET_NAME  = "SSCUIs"
OUTPUT_FILE = "sscui_export.xlsx"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def manual_login_wait(page: Page):
    print("\n" + "=" * 60)
    print("MANUELLER LOGIN")
    print("1. Bitte im Browser einloggen")
    print("2. Warte bis die Configuration-Liste sichtbar ist")
    print("3. Drücke dann hier ENTER")
    print("=" * 60)
    input()


# ---------------------------------------------------------------------------
# Expand-All
# ---------------------------------------------------------------------------

async def click_expand_all(page: Page) -> bool:
    """Klickt den 'Alle ausklappen' Button (↓≡ Icon im Screenshot)."""
    buttons = await page.evaluate("""
        () => Array.from(document.querySelectorAll('button, [role="button"]')).map(b => ({
            title:     b.getAttribute('title')      || '',
            ariaLabel: b.getAttribute('aria-label') || '',
            text:      b.innerText.trim().slice(0, 60),
            icon:      b.getAttribute('icon')       || '',
        }))
    """)

    expand_keywords = [
        'expand', 'flatten', 'ausklappen', 'alle',
        'expand all', 'expand-all', 'collapseall',
    ]

    for b in buttons:
        combined = (b['title'] + b['ariaLabel'] + b['text'] + b['icon']).lower()
        if any(kw in combined for kw in expand_keywords):
            selector = None
            if b['title']:
                selector = f'button[title="{b["title"]}"]'
            elif b['ariaLabel']:
                selector = f'[aria-label="{b["ariaLabel"]}"]'

            if selector:
                try:
                    await page.click(selector, timeout=5000)
                    print(f"  Expand-Button geklickt: '{b['title'] or b['ariaLabel'] or b['text']}'")
                    await asyncio.sleep(4)
                    return True
                except Exception:
                    continue

    return False


# ---------------------------------------------------------------------------
# Extraktion: sichtbare SSCUI-Zeilen
# ---------------------------------------------------------------------------

async def extract_visible_rows(page: Page) -> list:
    """Liest Name, ID und data-testid aller sichtbaren SSCUI-Zeilen.

    data-testid (z.B. 'titleTableCell_1.2.3') identifiziert jede Zeile
    eindeutig anhand ihres Baumpfads – unabhängig von Scroll-Position oder
    DOM-Reflow. Wird in Phase 2 als präziser CSS-Selektor zum Klicken genutzt.
    """
    return await page.evaluate("""
        () => {
            const results = [];
            const titleCells = document.querySelectorAll('span[data-testid^="titleTableCell_"]');
            titleCells.forEach((span) => {
                const ui5link = span.querySelector('ui5-link');
                if (!ui5link) return;
                const name = ui5link.innerText.trim();
                if (!name) return;

                const testId  = span.getAttribute('data-testid');
                const gridcell = span.closest('[role="gridcell"]');
                const rowIndex = gridcell ? gridcell.getAttribute('data-row-index') : null;
                if (rowIndex === null) return;

                const idCell = document.querySelector(
                    `[data-column-id-cell="externalId"][data-row-index="${rowIndex}"]`
                );
                const sscuiId = idCell ? idCell.innerText.trim() : '';
                if (!sscuiId || !/^\\d+$/.test(sscuiId)) return;

                results.push({ name, id: sscuiId, testId });
            });
            return results;
        }
    """)


# ---------------------------------------------------------------------------
# URL-Capture per testId-Selektor
# ---------------------------------------------------------------------------

async def click_and_get_url(page: Page, test_id: str) -> str:
    """Klickt den ui5-link einer spezifischen SSCUI-Zeile über ihren
    eindeutigen data-testid Selektor und fängt die URL via window.open-
    Interceptor ab.

    Kein expect_event/popup-wait – der Interceptor gibt null zurück, sodass
    nie ein Tab entsteht. 0.5s Wartezeit reicht für den JS-Handler.
    """
    locator = page.locator(f'span[data-testid="{test_id}"] ui5-link')
    try:
        # Interceptor frisch setzen (SPA kann window.open beim Scroll-Update überschreiben)
        await page.evaluate("""
            () => {
                window.__interceptedUrl = null;
                window.open            = (u, ...a) => { window.__interceptedUrl = u || ''; return null; };
                window.location.assign  = (u)       => { window.__interceptedUrl = u || ''; };
                window.location.replace = (u)       => { window.__interceptedUrl = u || ''; };
            }
        """)

        await locator.click(timeout=4000)
        await asyncio.sleep(0.5)

        url = await page.evaluate("() => window.__interceptedUrl || ''")
        if url:
            return url

        # Fallback: falls doch ein Tab geöffnet wurde
        for p in page.context.pages:
            if p != page:
                tab_url = p.url
                await p.close()
                if tab_url and tab_url != "about:blank":
                    return tab_url

        return ''
    except Exception:
        return ''


# ---------------------------------------------------------------------------
# Scroll & Sammeln
# ---------------------------------------------------------------------------

async def scroll_and_collect(page: Page) -> list:
    """Phase 1: Scrollt durch die Liste und sammelt Name + ID + testId aller SSCUIs.
       Phase 2: Scrollt erneut und klickt jeden Link per eindeutigem testId-Selektor."""

    viewport = page.viewport_size or {"width": 1280, "height": 800}
    table_x  = viewport["width"]  // 2
    table_y  = viewport["height"] // 2
    await page.mouse.move(table_x, table_y)

    # ── Phase 1: Name + ID + testId sammeln ────────────────────────────────
    collected = {}   # sscui_id → {name, id, testId, link}
    no_new    = 0
    step      = 0

    print("\nPhase 1: Sammle SSCUI Namen, IDs und testIds...")
    while no_new < 6:
        try:
            rows      = await extract_visible_rows(page)
            new_count = sum(1 for r in rows if r['id'] not in collected)
            for r in rows:
                if r['id'] not in collected:
                    collected[r['id']] = {
                        'name':   r['name'],
                        'id':     r['id'],
                        'testId': r['testId'],
                        'link':   '',
                    }

            print(f"  Schritt {step+1:>3}: {len(rows):>3} sichtbar | "
                  f"{new_count:>3} neu | {len(collected):>4} gesamt")

            no_new = no_new + 1 if new_count == 0 else 0
            await page.mouse.move(table_x, table_y)
            await page.mouse.wheel(0, 600)
            await asyncio.sleep(1.5)
            step += 1
            if step > 500:
                print("  Scroll-Limit erreicht.")
                break
        except Exception as e:
            print(f"\n  FEHLER in Phase 1, Schritt {step+1}: {e}")
            break

    print(f"\n  {len(collected)} SSCUIs gesammelt.")

    # ── Phase 2: URLs per testId-Selektor ermitteln ─────────────────────────
    print("\nPhase 2: Ermittle URLs (klicke jeden Link per eindeutigem testId)...")

    async def scroll_to_top():
        await page.mouse.move(table_x, table_y)
        for _ in range(50):
            await page.mouse.wheel(0, -3000)
            await asyncio.sleep(0.04)
        await asyncio.sleep(1.5)

    ids_without_url = {r['id'] for r in collected.values() if not r['link']}
    MAX_PASSES      = 5

    for pass_num in range(1, MAX_PASSES + 1):
        if not ids_without_url:
            break

        await scroll_to_top()
        check = await extract_visible_rows(page)
        print(f"\n  Pass {pass_num}/{MAX_PASSES}: {len(ids_without_url)} offen | "
              f"Startzeile ID={check[0]['id'] if check else '?'}")

        no_advance = 0
        step2      = 0

        while ids_without_url and no_advance < 25:
            try:
                rows         = await extract_visible_rows(page)
                rows_needing = [r for r in rows if r['id'] in ids_without_url]
                found        = 0

                for row in rows_needing:
                    # testId ist eindeutiger Baumpfad-Selektor → kein Re-Extract nötig,
                    # kein Positions-Drift nach vorherigen Klicks
                    url = await click_and_get_url(page, row['testId'])
                    if url:
                        collected[row['id']]['link'] = url
                        ids_without_url.discard(row['id'])
                        found += 1

                done  = len(collected) - len(ids_without_url)
                total = len(collected)
                print(f"  P{pass_num} Schritt {step2+1:>3}: {found:>2} URLs | "
                      f"{done:>4}/{total} | {len(ids_without_url):>4} offen | "
                      f"sichtbar {len(rows):>2} ({len(rows_needing):>2} zu klicken)")

                no_advance = no_advance + 1 if found == 0 else 0
                await page.mouse.move(table_x, table_y)
                await page.mouse.wheel(0, 400)
                await asyncio.sleep(1.2)
                step2 += 1
                if step2 > 600:
                    print("  Scroll-Limit erreicht.")
                    break
            except Exception as e:
                print(f"\n  FEHLER P{pass_num} Schritt {step2+1}: {e}")
                break

        print(f"  Pass {pass_num} fertig: {len(ids_without_url)} verbleibend")

    missing = len(ids_without_url)
    if missing:
        print(f"  {missing} SSCUIs ohne URL (werden ohne Link gespeichert).")

    return list(collected.values())


# ---------------------------------------------------------------------------
# Excel-Ausgabe
# ---------------------------------------------------------------------------

def write_excel(output_path: Path, items: list, reference_ids: set = None):
    """Schreibt SSCUI-Daten in Excel. Optional: Vollständigkeitsprüfung gegen reference_ids."""
    from datetime import datetime

    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME

    header_font  = Font(bold=True, color="FFFFFF")
    header_fill  = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    warning_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")

    headers = ["SSCUI Name", "SSCUI Nummer", "Link"]
    for col, h in enumerate(headers, start=1):
        cell      = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill

    crawled_ids = set()
    for row_idx, item in enumerate(items, start=2):
        ws.cell(row=row_idx, column=1, value=item['name'])
        ws.cell(row=row_idx, column=2, value=item['id'])
        ws.cell(row=row_idx, column=3, value=item['link'])
        for col in range(1, 4):
            ws.cell(row=row_idx, column=col).alignment = Alignment(vertical="top")
        if not item['link']:
            for col in range(1, 4):
                ws.cell(row=row_idx, column=col).fill = warning_fill
        crawled_ids.add(str(item['id']))

    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 100

    # Vollständigkeitsprüfung
    if reference_ids:
        missing = reference_ids - crawled_ids
        ws_miss = wb.create_sheet("Fehlend")
        ws_miss.cell(row=1, column=1, value="Fehlende SSCUI Nummer").font = header_font
        ws_miss.cell(row=1, column=1).fill = PatternFill(
            start_color="FF0000", end_color="FF0000", fill_type="solid")
        for i, mid in enumerate(sorted(missing), start=2):
            ws_miss.cell(row=i, column=1, value=mid)
        print(f"  Vollständigkeit: {len(crawled_ids)}/{len(reference_ids)} gecrawlt "
              f"| {len(missing)} fehlend → Sheet 'Fehlend'")

    no_url = sum(1 for it in items if not it['link'])
    if no_url:
        print(f"  Hinweis: {no_url} SSCUIs ohne URL (gelb markiert)")

    try:
        wb.save(output_path)
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_path.with_stem(output_path.stem + f"_{ts}")
        wb.save(output_path)
        print(f"  Datei gesperrt – gespeichert als: {output_path.name}")

    print(f"  {len(items)} SSCUIs gespeichert: {output_path.resolve()}")


# ---------------------------------------------------------------------------
# Haupt-Logik
# ---------------------------------------------------------------------------

async def run_crawler(output_path: Path, reference_ids: set = None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page    = await (await browser.new_context()).new_page()

        print(f"\nNavigiere zu: {CBC_URL}")
        try:
            await page.goto(CBC_URL, wait_until="commit", timeout=30000)
        except Exception:
            pass

        await manual_login_wait(page)

        print("Warte auf Seitenstabilisierung...")
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await asyncio.sleep(3)
        print(f"  Seite stabil: {page.url[:80]}")

        # Initialen Interceptor setzen (wird in click_and_get_url vor jedem Klick erneuert)
        await page.evaluate("""
            () => {
                window.__interceptedUrl = null;
                window.open = (u, ...a) => { window.__interceptedUrl = u || ''; return null; };
            }
        """)
        print("  window.open Interceptor aktiv.")

        print("\nVersuche alle Gruppen auszuklappen...")
        expanded = await click_expand_all(page)
        if not expanded:
            print("  Expand-Button nicht automatisch gefunden.")
            print("  Bitte den ↓≡ Button im Browser manuell klicken,")
            print("  warten bis alle Einträge geladen sind, dann ENTER drücken.")
            input()
        else:
            print("  Warte auf vollständiges Laden der Liste...")
            await asyncio.sleep(5)

        items = []
        try:
            items = await scroll_and_collect(page)
        except Exception as e:
            print(f"\nUnerwarteter Fehler beim Crawlen: {e}")
        finally:
            if items:
                print(f"\n{len(items)} SSCUIs gefunden – speichere...")
                write_excel(output_path, items, reference_ids)
            else:
                print("\nKeine SSCUIs gesammelt – nichts gespeichert.")
                print("Tipp: ENTER erst drücken wenn die Liste vollständig sichtbar ist.")

        try:
            await browser.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CBC SSCUI Crawler – extrahiert Namen, Nummern und Links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python cbc_crawler.py
  python cbc_crawler.py -o meine_sscuis.xlsx
        """,
    )
    parser.add_argument(
        "--output", "-o",
        default=OUTPUT_FILE,
        help=f"Ausgabe-Excel-Datei (Standard: {OUTPUT_FILE})",
    )
    parser.add_argument(
        "--reference", "-r",
        default=None,
        help="Excel/CSV mit Referenz-SSCUI-Nummern (Spalte A) zur Vollständigkeitsprüfung",
    )
    args = parser.parse_args()

    reference_ids = None
    ref_path = Path(args.reference) if args.reference else \
               Path(r"C:\Users\goeth\desktop\Crawling\Configure Your Business Processes(1).xlsx")

    if ref_path.exists():
        import pandas as pd
        df = pd.read_excel(ref_path)
        if 'ID' in df.columns:
            reference_ids = {str(int(v)) for v in df['ID'].dropna()}
        else:
            reference_ids = {str(v).strip() for v in df.iloc[:, 0].dropna()}
        print(f"Referenzliste geladen: {len(reference_ids)} IDs aus {ref_path.name}")
    else:
        print(f"Hinweis: Keine Referenzdatei gefunden ({ref_path.name}) – keine Vollständigkeitsprüfung.")

    asyncio.run(run_crawler(Path(args.output), reference_ids))


if __name__ == "__main__":
    main()
