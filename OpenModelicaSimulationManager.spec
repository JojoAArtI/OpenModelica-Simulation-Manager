# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\joeinarthur\\OpenModelica Simulation Manager\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\joeinarthur\\OpenModelica Simulation Manager\\resources', 'resources')],
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
    name='OpenModelicaSimulationManager',
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
    icon=['D:\\joeinarthur\\OpenModelica Simulation Manager\\resources\\icons\\openmodelica.ico'],
)
