"""Archive operations backed by 7z (extraction) and zipfile (creation)."""

import subprocess
import sys
import zipfile
from collections.abc import Iterable, Iterator
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


def unzip(source: Path, target: Path, *, silent: bool = True) -> int:
    stream = subprocess.DEVNULL if silent else None
    return subprocess.run(
        [_find_7z(), "x", str(source), f"-o{str(target)}", "-y"],
        stdout=stream,
        stderr=stream,
    ).returncode


def walk(
    root: Path,
    base: Path,
    prefix: str | None,
) -> Iterator[tuple[Path, str]]:
    """Walk root, yielding (filepath, arcname) pairs for each file.

    arcname = f"{prefix}/{child.relative_to(base)}" if prefix
              else child.relative_to(base).as_posix()
    """
    for child in sorted(root.rglob("*")):
        if child.is_file():
            rel = child.relative_to(base).as_posix()
            arcname = f"{prefix}/{rel}" if prefix else rel
            yield (child, arcname)


def zip(
    target: Path,
    entries: Iterable[tuple[Path, str]],
    *,
    level: int = 5,
) -> None:
    with zipfile.ZipFile(Path(target), "w", zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
        for filepath, arcname in entries:
            zf.write(str(filepath), arcname)
