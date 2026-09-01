# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

webdriver_manager_datas, webdriver_manager_binaries, webdriver_manager_hiddenimports = collect_all('webdriver_manager')
a = Analysis(
    ['app\\main.py'],
    pathex=[],
    binaries=webdriver_manager_binaries,
    datas=webdriver_manager_datas,
    hiddenimports=(
        ['openpyxl', 'pypdf']
        + collect_submodules('selenium')
        + webdriver_manager_hiddenimports
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WhatsApp Message Sender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
