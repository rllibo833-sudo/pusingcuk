# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    "evaluator",
    "parser",
    "lexer",
    "ast_nodes",
    "tools.formatter",
    "tools",
]
hiddenimports += collect_submodules("tools")

# Analysis(datas=...) requires (source, destination) pairs. Tree emits TOC
# entries with a different shape and fails with current PyInstaller releases.
datas = []
if os.path.isdir("examples"):
    for root, _dirs, filenames in os.walk("examples"):
        destination = os.path.relpath(root, ".")
        for filename in filenames:
            source = os.path.join(root, filename)
            datas.append((source, destination))

a = Analysis(
    ["pusingcuk_new.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="pusingcuk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
