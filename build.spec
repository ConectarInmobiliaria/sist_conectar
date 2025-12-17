# -*- mode: python ; coding: utf-8 -*-
# build.spec - Configuración para crear ejecutable de CONECTAR

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Datos adicionales que deben incluirse
datas = [
    ('imagenes', 'imagenes'),  # Incluir carpeta de imágenes (logo, favicon)
]

# Módulos ocultos que PyInstaller no detecta automáticamente
hiddenimports = [
    'customtkinter',
    'bcrypt',
    'supabase',
    'PIL._tkinter_finder',
    'tkcalendar',
    'reportlab',
    'reportlab.pdfgen.canvas',
    'reportlab.lib.pagesizes',
    'reportlab.lib.units',
    'reportlab.lib.colors',
    'reportlab.platypus',
    'dateutil',
    'dateutil.relativedelta',
    'babel.numbers',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CONECTAR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='imagenes/favicon.png' if os.path.exists('imagenes/favicon.png') else None,
)