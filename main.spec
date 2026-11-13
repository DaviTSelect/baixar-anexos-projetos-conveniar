# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

datas = (
    collect_data_files('customtkinter')
    + collect_data_files('certifi')
    + collect_data_files('selenium')
    + collect_data_files('openpyxl')
    + [('icon/logo.ico', 'icon')]
)

a = Analysis(
    ['src/main.py'],
    pathex=['src', '.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'version',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.options',
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
    a.binaries,
    a.datas,
    [],
    name='BaixarAnexosConveniar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon/logo.ico'],
)
