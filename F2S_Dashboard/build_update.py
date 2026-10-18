"""
build_update.py -- Baut ein kleines Update-ZIP (nur App-Code, kein Python/Browser).

Das ZIP enthaelt:
  app/            (ohne config.local.json und ohne __pycache__)
  Dashboard.html
  UPDATE.bat      (ersetzt beim Kollegen app/ + Dashboard.html, laesst
                   data/, python/, config.local.json unberuehrt)
  UPDATE_LIESMICH.txt

Aufruf:  python build_update.py
Ergebnis: F2S_Dashboard_Update_v<VERSION>.zip  (im Projektordner)
"""
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE / "app"


def app_version() -> str:
    txt = (APP / "refresh.py").read_text(encoding="utf-8")
    m = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', txt)
    return m.group(1) if m else "0.0.0"


UPDATE_BAT = r"""@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo  F2S Dashboard  -  Update einspielen
echo ================================================================
echo.
echo Dieses Update ersetzt nur den Programmcode (app-Ordner + Dashboard.html).
echo Ihre Daten (data-Ordner), die portable Python und Ihre
echo SharePoint-Einstellung (config.local.json) bleiben unveraendert.
echo.

REM Zielordner = der Ordner, in dem diese UPDATE.bat liegt (entpacktes Update).
REM Das Dashboard-Paket wird als uebergeordneter Zielordner erwartet, ODER
REM diese Dateien liegen bereits im Paketordner.

REM Sicherung der alten config.local.json (falls im Update enthalten - ist es nicht).
if not exist "app\" (
    echo !! Kein app-Ordner im Update gefunden. Abbruch.
    pause
    exit /b 1
)

echo Kopiere neue Dateien ...
xcopy /E /I /Y "app" "%TARGET%app\" >nul 2>&1

endlocal
"""


def build():
    version = app_version()
    out = HERE / f"F2S_Dashboard_Update_v{version}.zip"

    # UPDATE.bat: robustes Kopieren per PowerShell (sicherer als xcopy-Varianten).
    update_bat = (
        "@echo off\r\n"
        "setlocal\r\n"
        "chcp 65001 >nul\r\n"
        'cd /d "%~dp0"\r\n'
        "echo ================================================================\r\n"
        f"echo  F2S Dashboard  -  Update auf v{version}\r\n"
        "echo ================================================================\r\n"
        "echo.\r\n"
        "echo Dieses Update ersetzt nur den Programmcode (app + Dashboard.html).\r\n"
        "echo Ihre Daten (data), die portable Python und Ihre SharePoint-\r\n"
        "echo Einstellung (config.local.json) bleiben erhalten.\r\n"
        "echo.\r\n"
        'set /p TARGET="Pfad zum vorhandenen Dashboard-Ordner (Enter = uebergeordneter Ordner): "\r\n'
        'if "%TARGET%"=="" set "TARGET=.."\r\n'
        "echo.\r\n"
        'if not exist "%TARGET%\\app\\" (\r\n'
        '    echo !! Im Zielordner "%TARGET%" wurde kein app-Ordner gefunden.\r\n'
        "    echo    Bitte den Pfad zum entpackten Dashboard-Paket angeben.\r\n"
        "    pause\r\n"
        "    exit /b 1\r\n"
        ")\r\n"
        "echo Sichere vorhandene config.local.json ...\r\n"
        'if exist "%TARGET%\\app\\config.local.json" copy /Y "%TARGET%\\app\\config.local.json" "%TEMP%\\f2s_cfg_backup.json" >nul\r\n'
        "echo Spiele neuen Programmcode ein ...\r\n"
        'powershell -NoProfile -Command "Copy-Item -Path \'app\\*\' -Destination (Join-Path \'%TARGET%\' \'app\') -Recurse -Force"\r\n'
        'copy /Y "Dashboard.html" "%TARGET%\\Dashboard.html" >nul\r\n'
        "echo Stelle config.local.json wieder her ...\r\n"
        'if exist "%TEMP%\\f2s_cfg_backup.json" copy /Y "%TEMP%\\f2s_cfg_backup.json" "%TARGET%\\app\\config.local.json" >nul\r\n'
        "echo.\r\n"
        f"echo Fertig. Das Dashboard ist jetzt auf Version v{version}.\r\n"
        "echo Bitte Dashboard.html neu laden (bzw. Aktualisieren.bat ausfuehren).\r\n"
        "echo.\r\n"
        "pause\r\n"
        "endlocal\r\n"
    )

    liesmich = (
        "F2S Dashboard - Update v" + version + "\r\n"
        "========================================\r\n\r\n"
        "So spielen Sie das Update ein:\r\n\r\n"
        "1. Dieses ZIP in einen beliebigen Ordner entpacken.\r\n"
        "2. UPDATE.bat per Doppelklick starten.\r\n"
        "3. Wenn gefragt: den Pfad zu Ihrem vorhandenen Dashboard-Ordner\r\n"
        "   angeben (der Ordner mit Aktualisieren.bat und dem app-Ordner).\r\n"
        "   Liegt die UPDATE.bat direkt im uebergeordneten Ordner, einfach\r\n"
        "   Enter druecken.\r\n\r\n"
        "Was passiert:\r\n"
        "- Ersetzt wird NUR der Programmcode (app-Ordner + Dashboard.html).\r\n"
        "- UNVERAENDERT bleiben: Ihre Historie (data), die portable Python\r\n"
        "  und Ihre SharePoint-Einstellung (config.local.json).\r\n\r\n"
        "Nach dem Update Dashboard.html neu laden oder Aktualisieren.bat starten.\r\n"
        "Die Versionsnummer unten im Dashboard zeigt v" + version + ".\r\n"
    )

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        # app/ komplett, ausser config.local.json und __pycache__
        # Dateien, die der HTML-Weg nicht nutzt (alter Server-Modus) bzw. die
        # Nutzer-Einstellung, werden nicht mitgepackt.
        skip = {"config.local.json", "backend.py", "index.html"}
        for p in APP.rglob("*"):
            if p.is_dir():
                continue
            if "__pycache__" in p.parts:
                continue
            if p.name in skip:
                continue
            z.write(p, Path("app") / p.relative_to(APP))
        # Dashboard.html
        z.write(HERE / "Dashboard.html", "Dashboard.html")
        # Launcher + Anleitung
        z.writestr("UPDATE.bat", update_bat)
        z.writestr("UPDATE_LIESMICH.txt", liesmich)

    size_kb = out.stat().st_size / 1024
    print(f"OK -> {out.name}  ({size_kb:.0f} KB, Version {version})")


if __name__ == "__main__":
    build()
