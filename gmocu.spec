# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['gmocu.py'],
    pathex=[],
    binaries=[],
    datas=[('gmocu.sql', '.'), ('Downloads/templates/organisms_renamed.xlsx', 'Downloads/templates/'), ('Downloads/templates/nucleic_acid_features_renamed.xlsx', 'Downloads/templates/'), ('Downloads/Downloads.txt', 'Downloads/')],
    hiddenimports=['openpyxl.cell._writer'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gmocu',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gmocu',
)
app = BUNDLE(
    coll,
    name='GMOCU.app',
    icon='icon.ico',
    bundle_identifier=None,
)
