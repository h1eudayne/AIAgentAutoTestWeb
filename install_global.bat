@echo off
echo ========================================
echo AITEST GLOBAL INSTALLATION
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -e .

if errorlevel 1 (
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Creating command wrapper...
echo @echo off > aitest.bat
echo python "%~dp0aitest.py" %%* >> aitest.bat

echo.
echo [3/3] Installation complete!
echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo Option 1: Add to PATH (Recommended)
echo   1. Copy this path: %CD%
echo   2. Open System Properties ^> Environment Variables
echo   3. Edit 'Path' variable
echo   4. Add new entry with the path above
echo   5. Restart terminal
echo.
echo Option 2: Use from this directory
echo   Just run: aitest --url https://example.com
echo.
echo ========================================
echo.
pause
