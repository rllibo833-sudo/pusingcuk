# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.building.datastruct import Tree
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

datas = Tree("examples", prefix="examples") if os.path.isdir("examples") else []

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
