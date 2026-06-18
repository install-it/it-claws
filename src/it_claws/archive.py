import os
import subprocess
import sys
from pathlib import Path

import patoolib


def _find_7z() -> str:
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


def unzip(source: os.PathLike, target: os.PathLike, *, silent: bool = True) -> int:
    stream = subprocess.DEVNULL if silent else None
    return subprocess.run(
        [_find_7z(), "x", str(source), f"-o{str(target)}", "-y"],
        stdout=stream,
        stderr=stream,
    ).returncode


def zip(
    target: os.PathLike,
    source: os.PathLike,
    *,
    level: int = 5,
    silent: bool = True,
    include: list[os.PathLike] | None = None,
) -> int:
    args = [_find_7z(), "a", "-tzip", f"-mx={level}", str(target), str(source)]
    if include:
        args.extend(str(i) for i in include)
    stream = subprocess.DEVNULL if silent else None
    return subprocess.run(args, stdout=stream, stderr=stream).returncode
