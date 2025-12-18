@echo off
REM requirements.bat - Installs Python dependencies from requirements.txt
REM Run from project root: double-click or run `requirements.bat` in PowerShell/CMD

SETLOCAL ENABLEEXTENSIONS
set "PY=python"

:: Try to find python executable; prefer environment's python if available
where %PY% >nul 2>nul || (
	echo Python not found in PATH. Please install Python 3.x and make sure it's on PATH.
	pause
	exit /b 1
)

echo Upgrading pip...
%PY% -m pip install --upgrade pip
if errorlevel 1 (
	echo Warning: pip upgrade failed, continuing to install packages...
)

if not exist requirements.txt (
	echo requirements.txt not found in the current directory.
	echo Create a requirements.txt file or run this script from the project root.
	pause
	exit /b 1
)

echo Checking for conflicting Discord libraries...
%PY% -m pip show py-cord >nul 2>&1
if %errorlevel% equ 0 (
	echo Found py-cord installed. Removing to avoid conflicts with discord.py...
	%PY% -m pip uninstall -y py-cord
)

%PY% -m pip show discord >nul 2>&1
if %errorlevel% equ 0 (
	echo Found old discord library installed. Removing to avoid conflicts...
	%PY% -m pip uninstall -y discord
)

echo Installing required packages from requirements.txt...
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
	echo One or more packages failed to install. Run "%PY% -m pip install -r requirements.txt" manually for details.
	pause
	exit /b 1
)

echo All packages installed successfully.
ENDLOCAL
pause
