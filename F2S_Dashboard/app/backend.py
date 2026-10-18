"""
backend.py -- Minimaler lokaler HTTP-Server fuer das F2S Outcome Dashboard.

Nutzt ausschliesslich die Python-Standardbibliothek (kein Flask o. ae.).

Endpunkte:
  GET  /                 -> index.html (Dashboard)
  GET  /assets/...       -> statische Dateien
  GET  /api/snapshots    -> data/snapshots.json
  GET  /api/config       -> Frontend-relevante Teile der Mapping-Config
  POST /api/refresh      -> Download (lesend) -> Parse -> Aggregate -> Snapshot
                            -> Cleanup (try/finally). Liefert Status + Warnungen.

Konfiguration ueber config.local.json (SharePoint-Ordner-URL) oder --source,
um im Entwicklungsmodus lokale Dateien statt SharePoint zu verwenden.
"""
from __future__ import annotations

import sys
import json
import shutil
import argparse
import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Eigenes Verzeichnis in den Importpfad, damit der Start aus jedem
# Arbeitsverzeichnis funktioniert (z. B. 'python app/backend.py' aus dem
# Paket-Root). parser/aggregate/downloader liegen neben dieser Datei.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import parser as fs_parser
import aggregate as fs_aggregate

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
TEMP_DIR = PROJECT_DIR / "temp"
SNAPSHOTS = DATA_DIR / "snapshots.json"
CONFIG_PATH = APP_DIR / "mapping.config.json"
LOCAL_CONFIG = APP_DIR / "config.local.json"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".woff2": "font/woff2",
}

# Wird in main() gesetzt.
RUNTIME = {"source_dir": None, "folder_url": None}


def _now():
    # Nutzt lokale Zeit fuer run_id, UTC-ISO fuer timestamp.
    now = datetime.datetime.now()
    utc = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y%m%d-%H%M%S"), utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_config() -> dict:
    return fs_parser.load_config(CONFIG_PATH)


def _collect_source_files(cfg: dict, log) -> tuple[list[Path], str]:
    """Beschafft die Excel-Dateien in TEMP_DIR.

    - Entwicklungsmodus (RUNTIME['source_dir']): kopiert lokale F2S-Dateien.
    - Normalbetrieb: laedt per Download-Wrapper LESEND aus SharePoint.
    Gibt (dateiliste, quelle-beschreibung) zurueck.
    """
    prefix = cfg.get("file_prefix", "F2S")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    src = RUNTIME.get("source_dir")
    if src:
        src = Path(src)
        log(f">> Entwicklungsmodus: kopiere lokale Dateien aus {src}")
        found = []
        for p in src.rglob("*.xlsx"):
            if p.name.startswith(prefix) and not p.name.startswith("~$"):
                target = TEMP_DIR / p.name
                shutil.copy2(p, target)
                found.append(target)
                log(f"   kopiert: {p.name}")
        return found, f"lokal:{src}"

    folder_url = RUNTIME.get("folder_url")
    if not folder_url:
        raise RuntimeError(
            "Keine SharePoint-Ordner-URL konfiguriert. Bitte config.local.json "
            "mit {\"folder_url\": \"...\"} anlegen oder --source verwenden.")
    import downloader
    files = downloader.download_f2s_files(folder_url, TEMP_DIR, prefix, log=log)
    return files, "sharepoint"


def run_refresh() -> dict:
    """Fuehrt den kompletten Refresh-Ablauf aus. Cleanup immer im finally."""
    cfg = _load_config()
    logs: list[str] = []
    log = lambda m: logs.append(str(m))
    run_id, ts = _now()

    try:
        files, source = _collect_source_files(cfg, log)
        if not files:
            return {"ok": False, "error": "Keine F2S-Dateien gefunden.",
                    "logs": logs}

        parsed_list = []
        for f in files:
            try:
                parsed_list.append(fs_parser.parse_workbook(f, cfg))
                log(f">> ausgewertet: {f.name}")
            except Exception as e:
                log(f"!! Parsing-Fehler bei {f.name}: {e}")

        if not parsed_list:
            return {"ok": False, "error": "Keine Datei konnte ausgewertet werden.",
                    "logs": logs}

        snapshot = fs_aggregate.build_snapshot(parsed_list, run_id, ts, cfg)
        snapshot["source"] = source
        snapshot = fs_aggregate.append_snapshot(SNAPSHOTS, snapshot)
        log(f">> Snapshot gespeichert (run {run_id}, unchanged={snapshot['unchanged']}).")

        return {
            "ok": True,
            "run_id": run_id,
            "timestamp": ts,
            "files_processed": snapshot["files_processed"],
            "unchanged": snapshot["unchanged"],
            "warnings": snapshot["warnings"],
            "logs": logs,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "logs": logs}
    finally:
        # Temp-Ordner IMMER leeren -- auch bei Fehlern.
        _cleanup_temp(log)


def _cleanup_temp(log=lambda m: None):
    try:
        if TEMP_DIR.exists():
            for p in TEMP_DIR.iterdir():
                if p.is_file():
                    p.unlink()
                else:
                    shutil.rmtree(p, ignore_errors=True)
        log(">> Temp-Ordner geleert.")
    except Exception as e:
        log(f"!! Cleanup-Warnung: {e}")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # ruhiger Server

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _send_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self._send(404, b'{"error":"not found"}')
            return
        ctype = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self):
        route = self.path.split("?", 1)[0]
        if route == "/" or route == "/index.html":
            self._send_file(APP_DIR / "index.html")
        elif route == "/api/snapshots":
            if SNAPSHOTS.exists():
                self._send(200, SNAPSHOTS.read_bytes())
            else:
                self._send_json({"snapshots": []})
        elif route == "/api/config":
            cfg = _load_config()
            # Nur fuer das Frontend relevante Teile ausliefern.
            self._send_json({
                "status_keys": fs_aggregate.STATUS_KEYS,
                "main_types": fs_aggregate.MAIN_TYPES,
                "extra_types": fs_aggregate.EXTRA_TYPES,
                "fit_assessment_values": cfg.get("fit_assessment_values", []),
            })
        elif route.startswith("/assets/"):
            rel = route[len("/assets/"):]
            self._send_file(APP_DIR / "assets" / rel)
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        route = self.path.split("?", 1)[0]
        if route == "/api/refresh":
            result = run_refresh()
            self._send_json(result, 200 if result.get("ok") else 500)
        else:
            self._send(404, b'{"error":"not found"}')


def main():
    ap = argparse.ArgumentParser(description="F2S Dashboard Backend")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--source", help="Entwicklungsmodus: lokaler Ordner mit "
                                      "F2S-Excel-Dateien statt SharePoint.")
    ap.add_argument("--no-browser", action="store_true",
                    help="Browser nicht automatisch oeffnen.")
    args = ap.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    if args.source:
        RUNTIME["source_dir"] = args.source
    elif LOCAL_CONFIG.exists():
        with open(LOCAL_CONFIG, encoding="utf-8") as f:
            RUNTIME["folder_url"] = json.load(f).get("folder_url")

    url = f"http://localhost:{args.port}/"
    print("=" * 60)
    print(" F2S Outcome Dashboard")
    print("=" * 60)
    print(f" Laeuft auf: {url}")
    if RUNTIME.get("source_dir"):
        print(f" Quelle:     lokaler Ordner ({RUNTIME['source_dir']})")
    elif RUNTIME.get("folder_url"):
        print(" Quelle:     SharePoint (config.local.json)")
    else:
        print(" Quelle:     NICHT konfiguriert (config.local.json fehlt)")
    print(" Zum Beenden: Fenster schliessen oder Strg+C")
    print("=" * 60)

    if not args.no_browser:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
