# -*- mode: python ; coding: utf-8 -*-

import os

icon_path = "app.ico" if os.path.exists("app.ico") else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('jogos_vasco.json', '.'),
        ('jogos_futuros.json', '.'),
        ('listas_auxiliares.json', '.'),
        ('elenco_atual.json', '.'),
        ('jogadores_historico.json', '.'),
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
    name='StatsVasco',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=icon_path,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StatsVasco',
)
