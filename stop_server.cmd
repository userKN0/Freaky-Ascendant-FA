@echo off
REM Stop the MBII Dedicated Server and any processes with "godfinger" in the name
echo Stopping mbiided.x86.exe...

taskkill /IM mbiided.x86.exe /F 2>NUL
if %errorlevel% equ 0 (
    echo mbiided.x86.exe stopped successfully.
) else (
    echo No mbiided.x86.exe process found.
)

echo.
echo Stopping Python processes with "godfinger" in the name...
wmic process where "name='python.exe' and CommandLine like '%%godfinger%%'" delete 2>NUL
if %errorlevel% equ 0 (
    echo Python godfinger processes stopped successfully.
) else (
    echo No Python godfinger processes found.
)

echo.
echo Stopping batch processes with "godfinger" in the name...
wmic process where "name='cmd.exe' and CommandLine like '%%godfinger%%'" delete 2>NUL
if %errorlevel% equ 0 (
    echo Batch godfinger processes stopped successfully.
) else (
    echo No batch godfinger processes found.
)

pause
