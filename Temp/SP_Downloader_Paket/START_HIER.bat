@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

REM Browser-Binaries nach LOCALAPPDATA legen -- NICHT in den Paketordner.
REM Grund: Liegt das Paket in einem OneDrive-/SharePoint-synchronisierten
REM Ordner, stoert die Synchronisierung die Datei-Locks des Browsers.
REM LOCALAPPDATA wird nie synchronisiert und ist daher sicher.
set "PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\SP-Downloader\ms-playwright"
set "PYEXE=%~dp0python\python.exe"

echo ================================================================
echo  SharePoint Excel-Downloader
echo ================================================================
echo.

REM Beim ersten Start: Chromium-Browser herunterladen (einmalig, ca. 170 MB).
REM Marker-Datei zeigt an, dass die Installation bereits erfolgreich war.
if not exist "%PLAYWRIGHT_BROWSERS_PATH%\.installed" (
    echo Erster Start erkannt.
    echo Lade den Browser einmalig herunter ^(ca. 170 MB, braucht Internet^)...
    echo Das kann je nach Verbindung einige Minuten dauern.
    echo.
    "%PYEXE%" -m playwright install chromium
    if errorlevel 1 (
        echo.
        echo !! Browser-Download fehlgeschlagen. Bitte Internetverbindung pruefen
        echo    und START_HIER.bat erneut ausfuehren.
        echo.
        pause
        exit /b 1
    )
    if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
    echo ok> "%PLAYWRIGHT_BROWSERS_PATH%\.installed"
    echo.
    echo Browser installiert.
    echo.
)

"%PYEXE%" sp_downloader.py %*

endlocal
