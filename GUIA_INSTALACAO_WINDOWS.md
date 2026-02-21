# Guia Windows: Versao Full e Demo

## 1) Gerar os executaveis (desenvolvedor)

Pre-requisitos:
- Windows 10/11
- Python 3.12+
- `pip` funcionando no terminal

Passos:
1. Abra o `Prompt de Comando` na pasta do projeto.
2. (Opcional) Crie e ative uma venv:
   `python -m venv .venv`
   `.venv\Scripts\activate`
3. Instale o PyInstaller:
   `pip install pyinstaller matplotlib`
4. Rode o script de build:
   `build_windows.bat`

Arquivos gerados:
1. `dist\StatsVasco\StatsVasco.exe` (versao full)
2. `dist\StatsVascoDemo\StatsVascoDemo.exe` (versao demo)

Observacoes:
1. Se existir `app.ico` na raiz do projeto, ele sera usado como icone do `.exe`.
2. Os JSON iniciais sao embutidos no executavel pelos arquivos:
   `StatsVascoFullWindows.spec` e `StatsVascoDemoWindows.spec`.
3. No primeiro uso, o app copia os dados para:
   `%LOCALAPPDATA%\StatsVasco`
   Exemplo: `C:\Users\SeuUsuario\AppData\Local\StatsVasco`
4. Se quiser habilitar o calendario popup no executavel, instale tambem:
   `pip install tkcalendar`

## 2) Como o usuario final executa

### Versao Full
1. Abra `dist\StatsVasco`.
2. Execute `StatsVasco.exe`.

### Versao Demo
1. Abra `dist\StatsVascoDemo`.
2. Execute `StatsVascoDemo.exe`.

## 3) Aviso do Windows SmartScreen

Se aparecer aviso de seguranca:
1. Clique em `Mais informacoes`.
2. Clique em `Executar assim mesmo`.

Para distribuicao publica sem aviso, o ideal e assinar o executavel com certificado de codigo.
