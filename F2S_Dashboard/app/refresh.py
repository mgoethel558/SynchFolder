"""
refresh.py -- Standalone-Aktualisierung OHNE lokalen Server.

Ablauf (von Aktualisieren.bat aufgerufen):
  1. F2S-Excel-Dateien LESEND aus SharePoint in temp/ laden
     (oder --source <ordner> fuer lokale Testdateien).
  2. Auswerten + aggregieren.
  3. Snapshot an data/snapshots.json anhaengen (append-only).
  4. data/snapshots.js schreiben (window.F2S_DATA = {...}) -- damit die
     Dashboard.html die Daten per file:// laden kann (kein Server/CORS).
  5. temp/ leeren (try/finally, auch bei Fehlern).
  6. Dashboard.html im Standardbrowser oeffnen.

Rueckgabe-Code: 0 ok, 2 Teilerfolg/Fehler.
"""
from __future__ import annotations

import sys
import json
import shutil
import argparse
import datetime
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Windows-Konsole auf UTF-8, damit Sonderzeichen in Meldungen nicht crashen.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import parser as fs_parser
import aggregate as fs_aggregate

# Zentrale App-Version (fuer Release-Nachverfolgung + Dashboard-Anzeige).
APP_VERSION = "1.1.0"

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
TEMP_DIR = PROJECT_DIR / "temp"
SNAPSHOTS_JSON = DATA_DIR / "snapshots.json"
SNAPSHOTS_JS = DATA_DIR / "snapshots.js"
DASHBOARD_HTML = PROJECT_DIR / "Dashboard.html"
CONFIG_PATH = APP_DIR / "mapping.config.json"
LOCAL_CONFIG = APP_DIR / "config.local.json"


def _now():
    now = datetime.datetime.now()
    utc = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y%m%d-%H%M%S"), utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_js(store: dict, cfg: dict):
    """Schreibt data/snapshots.js mit window.F2S_DATA (Historie + Config-Teile)."""
    payload = {
        "store": store,
        "config": {
            "status_keys": fs_aggregate.STATUS_KEYS,
            "main_types": fs_aggregate.MAIN_TYPES,
            "extra_types": fs_aggregate.EXTRA_TYPES,
            "fit_assessment_values": cfg.get("fit_assessment_values", []),
        },
        "app_version": APP_VERSION,
        "generated_at": _now()[1],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    js = "window.F2S_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    SNAPSHOTS_JS.write_text(js, encoding="utf-8")


def _excluded(name: str, cfg: dict) -> bool:
    """True, wenn der Dateiname ein Ausschlussmuster enthaelt (z. B. TEMPLATE)."""
    patterns = cfg.get("exclude_filename_contains", [])
    up = name.upper()
    return any(pat.upper() in up for pat in patterns)


def _collect(cfg, source, log):
    """Gibt (dateiliste, source_urls) zurueck. source_urls: Dateiname -> Web-URL."""
    prefix = cfg.get("file_prefix", "F2S")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    if source:
        src = Path(source)
        log(f">> Testmodus: kopiere lokale Dateien aus {src}")
        found = []
        for p in src.rglob("*.xlsx"):
            if not p.name.startswith(prefix) or p.name.startswith("~$"):
                continue
            if _excluded(p.name, cfg):
                log(f"   (uebersprungen: {p.name})")
                continue
            tgt = TEMP_DIR / p.name
            shutil.copy2(p, tgt)
            found.append(tgt)
            log(f"   {p.name}")
        return found, {}
    # SharePoint
    folder_url = None
    if LOCAL_CONFIG.exists():
        folder_url = json.load(open(LOCAL_CONFIG, encoding="utf-8")).get("folder_url")
    if not folder_url:
        raise RuntimeError(
            "Keine SharePoint-URL. Bitte app/config.local.json mit "
            '{"folder_url": "..."} anlegen (siehe config.local.json.example).')
    import downloader
    files = downloader.download_f2s_files(folder_url, TEMP_DIR, prefix, log=log)
    source_urls = getattr(downloader.download_f2s_files, "last_source_urls", {})
    # Template-/Vorlagendateien ausschliessen (nach dem Download).
    kept = []
    for f in files:
        if _excluded(f.name, cfg):
            log(f"   (uebersprungen: {f.name})")
            try: f.unlink()
            except Exception: pass
        else:
            kept.append(f)
    return kept, source_urls


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="Testmodus: lokaler Ordner mit F2S-Dateien")
    ap.add_argument("--no-open", action="store_true", help="Dashboard nicht oeffnen")
    args = ap.parse_args()

    cfg = fs_parser.load_config(CONFIG_PATH)
    run_id, ts = _now()
    log = lambda m: print(m, flush=True)

    print("=" * 60)
    print(" F2S Dashboard  -  Aktualisierung")
    print("=" * 60)

    code = 0
    try:
        files, source_urls = _collect(cfg, args.source, log)
        if not files:
            print("!! Keine F2S-Dateien gefunden.")
            return 2
        parsed = []
        for f in files:
            try:
                res = fs_parser.parse_workbook(f, cfg)
                # Drill-down-Link je Eintrag setzen (sofern Web-URL bekannt).
                url = source_urls.get(f.name, "")
                if url:
                    for e in res["entries"]:
                        e["source_url"] = url
                parsed.append(res)
                log(f">> ausgewertet: {f.name}")
            except Exception as e:
                log(f"!! Parsing-Fehler bei {f.name}: {e}")
        if not parsed:
            print("!! Keine Datei konnte ausgewertet werden.")
            return 2

        snap = fs_aggregate.build_snapshot(parsed, run_id, ts, cfg)
        snap["source"] = "lokal" if args.source else "sharepoint"
        snap["app_version"] = APP_VERSION
        _, appended = fs_aggregate.append_snapshot(SNAPSHOTS_JSON, snap)

        # snapshots.js immer neu schreiben (auch wenn kein neuer Snapshot),
        # damit die Anzeige konsistent ist.
        store = json.load(open(SNAPSHOTS_JSON, encoding="utf-8")) \
            if SNAPSHOTS_JSON.exists() else {"snapshots": [snap]}
        _write_js(store, cfg)
        if appended:
            log(f">> Neuer Snapshot gespeichert. "
                f"{len(store['snapshots'])} Snapshot(s) insgesamt.")
        else:
            log(">> Keine Aenderung gegenueber dem letzten Snapshot -- "
                "kein neuer Eintrag (Historie unveraendert).")
        if snap.get("warnings"):
            log(f">> {len(snap['warnings'])} Hinweis(e) (unbekannte Werte).")
    except Exception as e:
        print(f"!! FEHLER: {e}")
        code = 2
    finally:
        # Temp IMMER leeren.
        try:
            if TEMP_DIR.exists():
                for p in TEMP_DIR.iterdir():
                    p.unlink() if p.is_file() else shutil.rmtree(p, ignore_errors=True)
            log(">> Temp-Ordner geleert.")
        except Exception as e:
            log(f"!! Cleanup-Warnung: {e}")

    if not args.no_open and DASHBOARD_HTML.exists():
        log(">> Oeffne Dashboard im Browser ...")
        webbrowser.open(DASHBOARD_HTML.resolve().as_uri())
    return code


if __name__ == "__main__":
    sys.exit(main())
