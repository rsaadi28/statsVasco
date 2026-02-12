# Guia Mac: Versão Full e Demo

## 1) Gerar os instaladores (você, desenvolvedor)

Pré-requisitos:
- macOS
- Python 3.12+
- `pyinstaller` instalado
- `app.icns` no projeto

Passos:
1. Abra o Terminal na pasta do projeto.
2. (Opcional) Ative sua venv.
3. Instale o PyInstaller, se necessário:
   `pip install pyinstaller`
4. Dê permissão para o script:
   `chmod +x build_mac.sh`
5. Rode:
   `./build_mac.sh`

Arquivos gerados:
1. `dist/StatsVasco.app` (versão full)
2. `dist/StatsVascoDemo.app` (versão demo)
3. `StatsVasco-Full.dmg` (instalador full)
4. `StatsVasco-Demo.dmg` (instalador demo)

Observação:
1. Os JSON iniciais já são embutidos no app via `StatsVascoFull.spec` e `StatsVascoDemo.spec`.
2. No primeiro uso, o app copia os dados para:
   `~/Library/Application Support/StatsVasco`

## 2) Como o usuário instala no Mac

### Versão Full
1. Abra `StatsVasco-Full.dmg`.
2. Arraste `StatsVasco.app` para `Applications`.
3. Abra o app pela pasta `Applications`.

### Versão Demo
1. Abra `StatsVasco-Demo.dmg`.
2. Arraste `StatsVascoDemo.app` para `Applications`.
3. Abra o app pela pasta `Applications`.

## 3) Primeira abertura (Gatekeeper)

Se o macOS bloquear por app não assinado:
1. Vá em `Ajustes do Sistema` -> `Privacidade e Segurança`.
2. Em Segurança, clique em `Abrir Mesmo Assim`.
3. Confirme a execução.

## 4) Publicação para clientes (recomendado)

Para evitar avisos de segurança:
1. Assine o app (`codesign`) com certificado Apple Developer ID.
2. Notarize (`notarytool`) e faça stapling.
3. Distribua os `.dmg` já assinados/notarizados.
