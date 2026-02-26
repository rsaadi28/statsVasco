# Guia Mac: Versão Full e Demo

## 1) Gerar os instaladores (você, desenvolvedor)

Pré-requisitos:
- macOS
- Python 3.12+
- `pyinstaller` instalado
- `app.icns` no projeto
- (Para distribuição sem bloqueios) certificado `Developer ID Application` e ferramentas Xcode (`codesign`, `xcrun`)

Passos:
1. Abra o Terminal na pasta do projeto.
2. (Opcional) Ative sua venv.
3. Instale o PyInstaller, se necessário:
   `pip install pyinstaller`
4. Dê permissão para o script:
   `chmod +x build_mac.sh`
5. Rode:
   `./build_mac.sh`

### Opções de build (recomendado)

`build_mac.sh` agora aceita variáveis de ambiente para arquitetura, assinatura e notarização.

Exemplos:

1. Build padrão (arquitetura nativa da sua máquina):
   `./build_mac.sh`

2. Build universal (`Intel + Apple Silicon`):
   `TARGET_ARCH=universal2 ./build_mac.sh`

3. Build universal + assinatura de app/DMG:
   `TARGET_ARCH=universal2 SIGN_APP=1 SIGN_DMG=1 CODESIGN_IDENTITY="Developer ID Application: Seu Nome (TEAMID)" ./build_mac.sh`

4. Build universal + assinatura + notarização (via perfil do `notarytool`, recomendado):
   `TARGET_ARCH=universal2 SIGN_APP=1 SIGN_DMG=1 NOTARIZE=1 NOTARYTOOL_PROFILE="notary-profile" CODESIGN_IDENTITY="Developer ID Application: Seu Nome (TEAMID)" ./build_mac.sh`

5. Build universal + assinatura + notarização (via credenciais):
   `TARGET_ARCH=universal2 SIGN_APP=1 SIGN_DMG=1 NOTARIZE=1 APPLE_ID="voce@exemplo.com" APPLE_TEAM_ID="TEAMID" APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx" CODESIGN_IDENTITY="Developer ID Application: Seu Nome (TEAMID)" ./build_mac.sh`

Observações importantes:
1. `TARGET_ARCH=universal2` exige Python + dependências compatíveis com `universal2`.
2. Se a notarização estiver ativa (`NOTARIZE=1`), o script faz `staple` automático no `.dmg`.
3. Você pode usar `ENTITLEMENTS_FILE=/caminho/arquivo.plist` se precisar de entitlements customizados.

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
1. Gere o app com `TARGET_ARCH=universal2` (reduz problema Intel/Apple Silicon).
2. Assine app e DMG com certificado Apple Developer ID.
3. Notarize com `notarytool` e faça stapling (o script já faz se `NOTARIZE=1`).
4. Distribua os `.dmg` já assinados/notarizados.
