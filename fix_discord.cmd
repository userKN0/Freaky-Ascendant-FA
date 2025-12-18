@echo off
REM fix_discord.cmd - Completely removes and reinstalls discord.py to fix conflicts
REM Run this if you encounter import errors with discord or app_commands

SETLOCAL ENABLEEXTENSIONS
set "PY=python"

echo ============================================================
echo Discord.py Clean Reinstall Script
echo ============================================================
echo.

:: Check for Python
where %PY% >nul 2>nul || (
	echo ERROR: Python not found in PATH. Please install Python 3.x and add it to PATH.
	pause
	exit /b 1
)

echo [1/5] Uninstalling all Discord packages...
%PY% -m pip uninstall -y discord discord.py py-cord 2>nul
if errorlevel 1 (
	echo Warning: Some packages may not have been installed.
) else (
	echo Done.
)
echo.

echo [2/5] Clearing pip cache...
%PY% -m pip cache purge >nul 2>&1
echo Done.
echo.

echo [3/5] Upgrading pip...
%PY% -m pip install --upgrade pip
echo Done.
echo.

echo [4/5] Installing discord.py (clean install)...
%PY% -m pip install --force-reinstall --no-cache-dir "discord.py>=2.1.0"
if errorlevel 1 (
	echo ERROR: Failed to install discord.py
	pause
	exit /b 1
)
echo Done.
echo.

echo [5/5] Verifying installation...
%PY% -c "from discord import app_commands; print('✓ discord.py installed successfully with app_commands support')"
if errorlevel 1 (
	echo ERROR: Verification failed. app_commands cannot be imported.
	pause
	exit /b 1
)
echo.

echo ============================================================
echo Discord.py has been successfully reinstalled!
echo You can now run update_bot.py
echo ============================================================

ENDLOCAL
pause
