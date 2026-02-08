@echo off
setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
set "CFG_BACKUP=%PROJECT_ROOT%\config.backup.json"
pushd "%PROJECT_ROOT%"

if exist "dist\remote_switch\config.json" (
  copy /Y "dist\remote_switch\config.json" "%CFG_BACKUP%" >nul
)

if not exist ".venv" (
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --clean --noconfirm remote_switch.spec

if exist "%CFG_BACKUP%" (
  if not exist "dist\remote_switch" mkdir "dist\remote_switch"
  copy /Y "%CFG_BACKUP%" "dist\remote_switch\config.json" >nul
  del "%CFG_BACKUP%"
)

popd
endlocal
