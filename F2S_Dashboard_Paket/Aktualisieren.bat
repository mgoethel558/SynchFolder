@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

REM Browser-Binaries + Login-Session nach LOCALAPPDATA (nicht in den Paketordner,
REM damit OneDrive-/SharePoint-Sync die Datei-Locks nicht stoert).
set "PLAYWRIGHT_BROWSERS_PATH=%LOCALAPPDATA%\F2S-Dashboard\ms-playwright"
set "SP_PROFILE_APP=F2S-Dashboard"
set "SP_DOWNLOADER_DIR=%~dp0"

REM Portable Python aus dem Paket, sonst System-Python.
if exist "%~dp0python\python.exe" (
    set "PYEXE=%~dp0python\python.exe"
) else (
    set "PYEXE=python"
)

echo ================================================================
echo  Fit-to-Standard Outcome Dashboard  -  Aktualisieren
echo ================================================================
echo.

REM Beim ersten Start: Chromium einmalig laden (ca. 170 MB, braucht Internet).
if not exist "%PLAYWRIGHT_BROWSERS_PATH%\.installed" (
    echo Erster Start erkannt.
    echo Lade den Browser einmalig herunter ^(ca. 170 MB, braucht Internet^)...
    echo.
    "%PYEXE%" -m playwright install chromium
    if errorlevel 1 (
        echo.
        echo !! Browser-Download fehlgeschlagen. Internetverbindung pruefen
        echo    und erneut ausfuehren.
        echo.
        pause
        exit /b 1
    )
    if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
    echo ok> "%PLAYWRIGHT_BROWSERS_PATH%\.installed"
    echo.
)

REM Aktualisierung ausfuehren: Download (lesend) -> Auswertung -> Dashboard oeffnen.
"%PYEXE%" app\refresh.py
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo Fertig. Das Dashboard sollte sich im Browser geoeffnet haben.
) else (
    echo Es gab ein Problem bei der Aktualisierung. Bitte Meldungen oben pruefen.
)
echo.
pause
endlocal
