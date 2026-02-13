@echo off
REM AITest Global Command Wrapper
REM This allows running 'aitest' from anywhere on Windows

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run aitest.py with all arguments
python "%SCRIPT_DIR%aitest.py" %*
