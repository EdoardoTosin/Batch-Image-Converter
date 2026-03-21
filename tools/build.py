#!/usr/bin/env python3
"""
Build a standalone one-file binary using Nuitka.

Usage (from project root):
    uv run python tools/build.py
"""
from __future__ import annotations

import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "src" / "batch_image_converter" / "__main__.py"
DIST = ROOT / "dist"


def _version() -> str:
    """Read __version__ from the package without importing it."""
    text = (ROOT / "src" / "batch_image_converter" / "__init__.py").read_text()
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not m:
        raise RuntimeError("__version__ not found in src/batch_image_converter/__init__.py")
    return m.group(1)


def main() -> None:
    DIST.mkdir(exist_ok=True)

    system = platform.system()
    ver = _version()
    # Windows version strings require four numeric components
    win_ver = ver if ver.count(".") == 3 else ver + ".0"
    binary_name = "batch-image-converter" + (".exe" if system == "Windows" else "")

    cmd: list[str] = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--include-package=PIL",
        "--include-package=typer",
        "--include-package=rich",
        f"--output-filename={binary_name}",
        f"--output-dir={DIST}",
        "--assume-yes-for-downloads",
        "--remove-output",
    ]

    if system == "Windows":
        cmd += [
            "--windows-console-mode=attach",
            "--windows-product-name=Batch Image Converter",
            f"--windows-product-version={win_ver}",
            "--windows-file-description=Batch Image Converter",
            f"--windows-file-version={win_ver}",
        ]
    elif system == "Darwin":
        cmd += [
            "--macos-app-name=Batch Image Converter",
            f"--macos-app-version={ver}",
        ]

    cmd.append(str(ENTRY))

    print(f"Building Batch Image Converter {ver} for {system}...")
    subprocess.run(cmd, check=True)
    print(f"\nBinary: {DIST / binary_name}")


if __name__ == "__main__":
    main()
