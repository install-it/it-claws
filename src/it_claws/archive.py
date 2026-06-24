"""Archive operations backed by libarchive-c.

Extraction uses the low-level FFI read API so we can write entries
directly to an arbitrary target directory without ``os.chdir()``.
ZIP creation uses ``file_writer`` with per-file ``arcname`` control,
streaming file contents in chunks to support multi-GB driver packages.
"""

import logging
import os
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_CHUNK_SIZE = int(os.environ.get("IC_CHUNK_SIZE", 1024 * 64))


# Prime libarchive at load time
if getattr(sys, "frozen", False):
    base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    base = Path(__file__).parents[1]
bundled = base / "bin" / "libarchive" / "libarchive.dll"
if bundled.exists():
    os.environ.setdefault("LIBARCHIVE", str(bundled))

try:
    import libarchive.ffi as _ffi  # noqa: E402, F401 – triggers ctypes load
except OSError as exc:
    raise ImportError(
        "libarchive shared library not found. "
        "Set the LIBARCHIVE environment variable to the full path "
        "to libarchive.dll / libarchive.so, or install the system "
        "package (e.g. apt install libarchive13)."
    ) from exc

import libarchive as la  # noqa: E402
from libarchive.entry import FileType  # noqa: E402
from libarchive.ffi import (  # noqa: E402
    entry_clear,
    entry_new,
    read_data_into_memory,
    read_data_skip,
    read_free,
    read_new,
    read_next_header2,
    read_open_filename,
)


def unzip(source: os.PathLike, target: os.PathLike) -> None:
    """Extract *source* archive into *target* directory.

    Uses the low-level FFI read API so we can write entries directly to
    *target* without changing the working directory (thread-safe).
    """
    source = Path(source)
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)

    read_p = read_new()
    entry_p: int | None = None
    try:
        read_open_filename(read_p, str(source), 10240)
        entry_p = entry_new()
        while read_next_header2(read_p, entry_p) == 0:
            clean = os.fsdecode(la.ffi.entry_pathname(entry_p))
            clean = clean.replace("\\", "/")
            clean = re.sub(r"^[A-Za-z]:", "", clean)
            clean = clean.lstrip("/")

            # Security: skip absolute-or-traversal paths
            if not clean or clean.startswith(".."):
                read_data_skip(read_p)
                continue

            file_type = la.ffi.entry_filetype(entry_p)
            dest = target / clean

            if file_type == FileType.DIRECTORY:
                dest.mkdir(parents=True, exist_ok=True)
                read_data_skip(read_p)
            elif file_type in (FileType.REGULAR, FileType.REGULAR_1):
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as fh:
                    while True:
                        buf = read_data_into_memory(read_p, _CHUNK_SIZE)
                        if not buf:
                            break
                        fh.write(buf)
            else:
                # Symlinks, devices, etc. — skip
                read_data_skip(read_p)
    finally:
        if entry_p is not None:
            entry_clear(entry_p)
        read_free(read_p)


def _normalise_source_path(source: str) -> str:
    """Normalise a host path into a forward-slash archive path.

    Strips root slashes, Windows drive letters, and immediate ``./``.
    """
    p = source.replace("\\", "/")
    p = re.sub(r"^[A-Za-z]:", "", p)
    p = p.lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p


def zip(
    target: os.PathLike,
    source: os.PathLike,
    *,
    level: int = 5,
    zip_prefix: str | None = None,
    zip_includes: list[str] | None = None,
    manifest_path: os.PathLike | None = None,
) -> None:
    """Create a ZIP archive at *target* from *source* directory."""
    target = Path(target)
    source = Path(source)
    target.parent.mkdir(parents=True, exist_ok=True)

    output_dir_name = source.name if source.is_dir() else None

    # Collect entries from the main output directory
    all_entries: list[tuple[Path, str]] = []
    if source.is_dir():
        for child in sorted(source.rglob("*"), key=str):
            if child.is_dir():
                continue
            all_entries.append((child, child.relative_to(source.parent).as_posix()))

    # Collect entries from --zip-include
    include_no_layout: list[tuple[Path, str]] = []
    include_with_layout: list[tuple[Path, str]] = []

    if zip_includes:
        for arg in zip_includes:
            if "=" in arg:
                raw_source, layout = arg.split("=", 1)
            else:
                raw_source, layout = arg, None

            # Prevent path traversal without explicit re-anchor
            if layout is None and ".." in Path(raw_source).parts:
                raise ValueError(
                    f"Source path '{raw_source}' contains '..' — "
                    f"provide an explicit layout (source=layout) to safely "
                    f"re-anchor the entry, or use a path without parent "
                    f"directory references."
                )
            resolved_source = Path(raw_source).resolve()

            arc_root = layout if layout is not None else _normalise_source_path(raw_source)

            if resolved_source.is_dir():
                for child in sorted(resolved_source.rglob("*"), key=str):
                    if child.is_dir():
                        continue
                    arc = arc_root + "/" + child.relative_to(resolved_source).as_posix()
                    if layout is not None:
                        include_with_layout.append((child, arc))
                    else:
                        include_no_layout.append((child, arc))
            elif resolved_source.is_file():
                if layout is not None:
                    arc = layout + resolved_source.name if layout.endswith("/") else layout
                else:
                    arc = _normalise_source_path(raw_source)
                if layout is not None:
                    include_with_layout.append((resolved_source, arc))
                else:
                    include_no_layout.append((resolved_source, arc))
            else:
                logger.warning("zip-include source not found, skipping: %s", raw_source)

    # Prefix transformation
    # Prefix applies to main entries AND zip-include entries without explicit layout
    entries_to_prefix = all_entries + include_no_layout
    if zip_prefix is not None:
        prefix = zip_prefix.rstrip("/") + "/"
        all_entries = [(disk, prefix + arc.lstrip("/")) for disk, arc in entries_to_prefix]
    elif output_dir_name is not None:
        strip = output_dir_name.rstrip("/") + "/"
        all_entries = []
        for disk, arc in entries_to_prefix:
            adjusted = arc[len(strip) :] if arc.startswith(strip) else arc
            all_entries.append((disk, adjusted))
    else:
        all_entries = entries_to_prefix

    # zip-include entries WITH explicit layout are not affected by prefix
    all_entries.extend(include_with_layout)

    if manifest_path is not None:
        manifest = Path(manifest_path)
        if manifest.exists():
            all_entries = [(d, a) for d, a in all_entries if a != "manifest.json"]
            all_entries.append((manifest, "manifest.json"))

    # Deduplicate by arcname (last-wins)
    deduped: dict[str, Path] = {}
    for disk, arc in all_entries:
        if arc in deduped:
            logger.warning(
                "Duplicate archive path '%s': overriding '%s' with '%s'",
                arc,
                deduped[arc],
                disk,
            )
        deduped[arc] = disk

    with la.file_writer(str(target), "zip", options=f"compression-level={level}") as archive:
        for arc, disk in deduped.items():
            archive.add_files(str(disk), pathname=arc)
