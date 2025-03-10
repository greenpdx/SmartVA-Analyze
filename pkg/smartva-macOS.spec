# -*- mode: python -*-

a = Analysis(
    ['app.py'],
    pathex=['src/'],
    binaries=[],
    datas=[('src/smartva/res', './res'), ('src/smartva/data', './data')],
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
    a.binaries,
    a.datas,
    [],
    name='SmartVA-Analyze',
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
    icon=['pkg/icon.png'],
)
app = BUNDLE(
    exe,
    name='SmartVA-Analyze.app',
    icon='pkg/icon.png',
    bundle_identifier=None,
)
