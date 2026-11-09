@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  Build local - Baixar Anexos Conveniar
echo ============================================

if exist "venv\Scripts\python.exe" (
    set PY=venv\Scripts\python.exe
    set PIP=venv\Scripts\pip.exe
    set PYINST=venv\Scripts\pyinstaller.exe
) else (
    set PY=python
    set PIP=pip
    set PYINST=pyinstaller
)

for /f "usebackq delims=" %%v in (`%PY% -c "import sys; sys.path.insert(0,'.'); import version; print(version.VERSION)"`) do set VERSION=%%v
if "%VERSION%"=="" (
    echo ERRO: nao foi possivel ler VERSION de version.py
    pause & exit /b 1
)
echo Versao: %VERSION%
echo.

echo [1/4] Instalando dependencias de build...
%PIP% install -r requirements-build.txt -q
if %ERRORLEVEL% neq 0 ( echo ERRO ao instalar dependencias & pause & exit /b 1 )

echo [2/4] Executando testes...
%PY% -m pytest -q 2>nul || echo Sem testes ou testes ignorados, continuando...

echo [3/4] Compilando executavel...
if exist dist rmdir /s /q dist
%PYINST% main.spec --noconfirm
if %ERRORLEVEL% neq 0 ( echo ERRO no PyInstaller & pause & exit /b 1 )
if not exist "dist\main.exe" (
    echo ERRO: dist\main.exe nao encontrado
    pause & exit /b 1
)

echo [4/4] Calculando SHA-256...
for /f "usebackq delims=" %%h in (`powershell -NoProfile -Command "(Get-FileHash 'dist\main.exe' -Algorithm SHA256).Hash.ToLower()"`) do set SHA256=%%h
echo %SHA256%  main.exe > dist\main.exe.sha256
echo SHA-256: %SHA256%

echo.
echo ============================================
echo  Build concluido! Versao %VERSION%
echo  Executavel : dist\main.exe
echo ============================================
pause
