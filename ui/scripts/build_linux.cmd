@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%build_linux.sh"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

set "MODE=%~1"
if /i "%MODE%"=="docker" goto :docker
if /i "%MODE%"=="wsl" goto :wsl
if "%MODE%"=="" goto :wsl
goto :usage

:wsl

where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: wsl.exe not found. Install WSL and try again.
  exit /b 1
)

for /f "delims=" %%p in ('wsl wslpath -a "%SCRIPT_PATH%" 2^>nul') do set "WSL_SCRIPT=%%p"
if not defined WSL_SCRIPT (
  echo ERROR: Failed to convert path for WSL: "%SCRIPT_PATH%"
  exit /b 1
)

if defined WSL_DISTRO (
  set "WSL_CMD=wsl -d %WSL_DISTRO%"
) else (
  set "WSL_CMD=wsl"
)

%WSL_CMD% bash -lc "chmod +x '%WSL_SCRIPT%' && '%WSL_SCRIPT%'"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo ERROR: Linux build failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%

:docker
where docker.exe >nul 2>&1
if errorlevel 1 (
  echo ERROR: docker.exe not found. Install Docker Desktop and try again.
  exit /b 1
)

docker run --rm ^
  -v "%PROJECT_ROOT%:/work" ^
  -w /work ^
  python:3.11-slim ^
  bash -lc "apt-get update && apt-get install -y git binutils && ./scripts/build_linux.sh"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo ERROR: Linux build failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%

:usage
echo Usage: %~nx0 [wsl^|docker]
exit /b 1
