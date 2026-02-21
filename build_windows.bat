@echo off
setlocal enabledelayedexpansion

echo [1/3] Limpando builds antigas...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] Gerando executavel Full...
pyinstaller StatsVascoFullWindows.spec
if errorlevel 1 (
  echo Falha ao gerar a versao Full.
  exit /b 1
)

echo [3/3] Gerando executavel Demo...
pyinstaller StatsVascoDemoWindows.spec
if errorlevel 1 (
  echo Falha ao gerar a versao Demo.
  exit /b 1
)

echo Concluido.
echo Pastas geradas:
echo  - dist\StatsVasco
echo  - dist\StatsVascoDemo
echo Executaveis:
echo  - dist\StatsVasco\StatsVasco.exe
echo  - dist\StatsVascoDemo\StatsVascoDemo.exe
