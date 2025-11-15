Rodar no macOS

1) cd /Users/rodrigo/Documents/pessoal/Sistemas/minha_grana_2025
   (se ainda não fizer parte da sessão atual) 

2) python3.12 -m venv .venv

3) source .venv/bin/activate

4) pip install --upgrade pip

5) (apenas uma vez) pip install -r requirements.txt
Se não tiver requirements, instale o que usa: pip install tk pyinstaller etc.

6) python main.py → abre o app usando o Tk 9.0.3.

Gerar instalador com PyInstaller dentro da venv
1) pip install pyinstaller

2) (opcional para ícone macOS) sips -s format icns app.ico --out app.icns script:

mkdir -p MinhaGrana.iconset
# gera as versões 1x e 2x exigidas pelo macOS
for size in 16 32 64 128 256 512; do
  double=$((size * 2))
  sips -z $size $size app.ico --out MinhaGrana.iconset/icon_${size}x${size}.png >/dev/null
  sips -z $double $double app.ico --out MinhaGrana.iconset/icon_${size}x${size}@2x.png >/dev/null
done
# tamanho especial 1024
sips -z 1024 1024 app.ico --out MinhaGrana.iconset/icon_512x512@2x.png >/dev/null

iconutil -c icns MinhaGrana.iconset -o app.icns
rm -r MinhaGrana.iconset


3) pyinstaller MinhasDividas.spec
ou pyinstaller --name MinhasDividas --windowed --icon app.icns main.py

4) Resultado fica em dist/MinhasDividas/ (ou .app se usar --windowed).
Execute para testar: ./dist/MinhasDividas/MinhasDividas (ou abra dist/MinhasDividas.app).

Quando terminar, saia do venv com deactivate.

# Para abrir o Application Support:
open ~/Library/"Application Support"