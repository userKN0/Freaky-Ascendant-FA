@echo off
REM verify_start.cmd - Verify that mbiided.x86.exe IS running
REM Exits with 0 if server is running, 1 if not running

tasklist /FI "IMAGENAME eq mbiided.x86.exe" 2>NUL | find /I /N "mbiided.x86.exe">NUL
if %errorlevel% equ 0 (
    REM Process is running
    exit /b 0
) else (
    REM Process is not running
    exit /b 1
)
