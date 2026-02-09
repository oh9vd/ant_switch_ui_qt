@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
set "CFG_BACKUP=%PROJECT_ROOT%\config.backup.json"
set "DIST_BASE=%PROJECT_ROOT%\dist\windows"
set "DIST_APP=%DIST_BASE%\remote_switch"
pushd "%PROJECT_ROOT%"

if exist "%DIST_APP%\config.json" (
  copy /Y "%DIST_APP%\config.json" "%CFG_BACKUP%" >nul
)

if not exist "%DIST_BASE%" mkdir "%DIST_BASE%"

if not exist ".venv" (
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

for /f %%i in ('git rev-parse --short HEAD 2^>nul') do set "APP_GIT_COMMIT=%%i"
if not defined APP_GIT_COMMIT set "APP_GIT_COMMIT=unknown"
echo %APP_GIT_COMMIT%> "version.txt"

pyinstaller --clean --noconfirm --distpath "%DIST_BASE%" --workpath "build\windows" remote_switch.spec

if exist "version.txt" del "version.txt"

if exist "%CFG_BACKUP%" (
  if not exist "%DIST_APP%" mkdir "%DIST_APP%"
  copy /Y "%CFG_BACKUP%" "%DIST_APP%\config.json" >nul
  del "%CFG_BACKUP%"
)


set "ARCHIVE_BASE=%DIST_BASE%\remote_switch-%APP_GIT_COMMIT%-windows"
echo INFO: Creating archive "%ARCHIVE_BASE%.7z"...
if exist "%DIST_APP%" (
  set "SEVEN_ZIP="
  for %%p in ("%ProgramFiles%\7-Zip\7z.exe" "%ProgramFiles(x86)%\7-Zip\7z.exe") do (
    if exist "%%~p" set "SEVEN_ZIP=%%~p"
  )
  if not defined SEVEN_ZIP (
    for /f "delims=" %%p in ('where 7z 2^>nul') do set "SEVEN_ZIP=%%p"
  )
  if defined SEVEN_ZIP (
    "!SEVEN_ZIP!" a -t7z "%ARCHIVE_BASE%.7z" "%DIST_APP%\*" >nul
  ) else (
    echo WARNING: 7z not found. Skipping archive creation.
  )
)
echo INFO: Build complete. Output directory: "%DIST_APP%"

popd
endlocal
