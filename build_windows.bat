@echo off
setlocal enabledelayedexpansion

echo [0/4] Validando dependencias de build...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
  echo PyInstaller nao encontrado. Rode: pip install pyinstaller
  exit /b 1
)

python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
  echo matplotlib nao encontrado. Rode: pip install matplotlib
  exit /b 1
)

echo [1/4] Limpando builds antigas...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/4] Gerando executavel Full...
pyinstaller StatsVascoFullWindows.spec
if errorlevel 1 (
  echo Falha ao gerar a versao Full.
  exit /b 1
)

echo [3/4] Gerando executavel Demo...
pyinstaller StatsVascoDemoWindows.spec
if errorlevel 1 (
  echo Falha ao gerar a versao Demo.
  exit /b 1
)

echo [4/4] Concluido.
echo Pastas geradas:
echo  - dist\StatsVasco
echo  - dist\StatsVascoDemo
echo Executaveis:
echo  - dist\StatsVasco\StatsVasco.exe
echo  - dist\StatsVascoDemo\StatsVascoDemo.exe
