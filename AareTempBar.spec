# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import tomllib

ROOT = Path(SPECPATH)


def _read_version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


a = Analysis(
    ["scripts/AareTempBar.py"],
    pathex=["src"],
    hiddenimports=[
        "rumps",
        "httpx",
        "pydantic",
        "anyio",
        "certifi",
        "h11",
        "httpcore",
        "idna",
        "sniffio",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AareTempBar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name="AareTempBar.app",
    icon=None,
    bundle_identifier="ch.jl115.aare-temp-menubar",
    info_plist={
        "CFBundleName": "AareTempBar",
        "CFBundleDisplayName": "AareTempBar",
        "CFBundleShortVersionString": _read_version(),
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
)
