# -*- mode: python ; coding: utf-8 -*-

from PIL import Image
from os.path import exists
import sys
from svg2png import svg2png

if not exists('logo.png'):
    try:
        svg2png('logo.svg')
    except:
        pass
if not exists('logo.ico'):
    image = Image.open('logo.png')

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    resized_images = [image.resize(size, Image.BICUBIC) for size in sizes]

    resized_images[0].save('logo.ico', format='ICO', sizes=sizes, append_images=[img for img in resized_images[1:]])

a = Analysis(
    ['chatbot_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.svg', '.'),
        ('logo.png', '.'),
        ('logo.ico', '.')
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
    name='chatbot_ui',
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
    icon='./logo.ico'
)