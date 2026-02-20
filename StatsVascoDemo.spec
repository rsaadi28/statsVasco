# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_demo.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('jogos_vasco.json', '.'),
        ('jogos_futuros.json', '.'),
        ('listas_auxiliares.json', '.'),
        ('elenco_atual.json', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StatsVascoDemo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StatsVascoDemo',
)
app = BUNDLE(
    coll,
    name='StatsVascoDemo.app',
    icon='app.icns',
    bundle_identifier='com.statsvasco.demo',
)
