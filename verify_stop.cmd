@echo off
REM verify_stop.cmd - Verify that mbiided.x86.exe is NOT running
REM Exits with 0 if server is stopped, 1 if still running

tasklist /FI "IMAGENAME eq mbiided.x86.exe" 2>NUL | find /I /N "mbiided.x86.exe">NUL
if %errorlevel% equ 0 (
    REM Process is still running
    exit /b 1
) else (
    REM Process is stopped
    exit /b 0
)
