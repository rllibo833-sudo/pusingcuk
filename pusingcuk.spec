# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.datastruct import Tree

a = Analysis(
    ["pusingcuk_new.py"],
    pathex=[],
    binaries=[],
    datas=Tree("examples", prefix="examples"),
    hiddenimports=["evaluator", "parser", "tools.formatter"],
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
