@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0enviar.ps1"
set "resultado=%errorlevel%"
echo.
pause
exit /b %resultado%
