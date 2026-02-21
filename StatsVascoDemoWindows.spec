# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

icon_path = "app.ico" if os.path.exists("app.ico") else None
matplotlib_datas = collect_data_files("matplotlib")

a = Analysis(
    ['main_demo.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('jogos_vasco.json', '.'),
        ('jogos_futuros.json', '.'),
        ('listas_auxiliares.json', '.'),
        ('elenco_atual.json', '.'),
        ('jogadores_historico.json', '.'),
    ] + matplotlib_datas,
    hiddenimports=[
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends._backend_tk',
    ],
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
    icon=icon_path,
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
