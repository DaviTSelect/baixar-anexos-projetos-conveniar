@echo off
python "%~dp0enviar.py"
set "resultado=%errorlevel%"
echo.
pause
exit /b %resultado%
