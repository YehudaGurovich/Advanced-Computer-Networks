# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mitm_packets.py'],
    pathex=['C:\\Users\\yehug\\Desktop\\JCT\\5784 - Sem B\\Advanced Computer Networks\\Labs\\Final Assignment\\src'],
    binaries=[],
    datas=[('encryption.py', '.'), ('utils.py', '.'),('messages.json', '.'), ('parameters.json', '.')],  # Include any necessary files here
    hiddenimports=['json'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='packets',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
