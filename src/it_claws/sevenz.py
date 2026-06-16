import sys
from pathlib import Path

import patoolib


def find_7z() -> str:
    if getattr(sys, "frozen", False):
        bundled = Path(sys.executable).parent / "bin" / "7zip" / "7za.exe"
    else:
        bundled = Path(__file__).parents[1] / "bin" / "7zip" / "7za.exe"

    if bundled.exists():
        return str(bundled)

    try:
        return patoolib.find_archive_program("7z", "extract")
    except Exception:
        pass

    return "7z"
