@echo off
REM Ableton VST Auditor - Windows Launcher
REM Double-click this file to run the GUI version

echo Starting Ableton VST Auditor...
echo.

REM Try python command first
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using python command
    python ableton_vst_audit.py
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using python3 command
    python3 ableton_vst_audit.py
    goto :end
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using py launcher
    py ableton_vst_audit.py
    goto :end
)

echo ERROR: Python not found!
echo Please install Python from https://python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
goto :end

:end
echo.
echo Press any key to exit...
pause >nul