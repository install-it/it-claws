"""Handling archive operations.
"""

import glob
import os
import subprocess
import zipfile
from abc import ABC
from pathlib import Path

import patoolib


class Archive(ABC):

    def unzip(self, source: os.PathLike, target: os.PathLike, silent: bool = True) -> int:
        """Extract a zip archive to the specified target directory.

        Args:
            source (os.PathLike): Path to the zip file.
            target (os.PathLike): Directory to extract files to.
            silent (bool): Suppress console output if True. Defaults to True.

        Returns:
            int: Exit code of the extraction process (0 for success).
        """

    def zip(self, target: os.PathLike, *source: os.PathLike, level: int = 5, silent: bool = True) -> int:
        """Create a zip archive from source files or directories.

        Args:
            target (os.PathLike): Path for the output zip file.
            *source (os.PathLike): Paths to files or directories to archive.
            level (int): Compression level (0-9). Defaults to 5.
            silent (bool): Suppress console output if True. Defaults to True.

        Returns:
            int: Exit code of the compression process (0 for success).
        """


class Archive7zip(Archive):

    path_7zip = Path(__file__).parents[1].joinpath('bin', '7zip', '7za.exe')

    def __init__(self):
        super().__init__()

        if not self.path_7zip.exists():
            self.path_7zip = patoolib.find_archive_program('7z', 'extract')

    def unzip(self, source, target, silent=True):
        stream = subprocess.DEVNULL if silent else None
        return subprocess.run(
            (self.path_7zip, 'x', str(source), f'-o{target}'),
            stdout=stream, stderr=stream
        ).returncode

    def zip(self, target, *source, level=5, silent=True):
        stream = subprocess.DEVNULL if silent else None
        return subprocess.run(
            (self.path_7zip, 'a', str(target),
             *source, f'-mx{level}'),
            stdout=stream, stderr=stream
        ).returncode


class ArchivePowershell(Archive):

    def unzip(self, source, target, silent=True):
        stream = subprocess.DEVNULL if silent else None
        return subprocess.run(
            ('powershell', 'Expand-Archive', '-Path',
             str(source), '-DestinationPath', f'"{target}"'),
            stdout=stream, stderr=stream
        ).returncode

    def zip(self, target, *source, level=5, silent=True):
        stream = subprocess.DEVNULL if silent else None
        return subprocess.run(
            (
                'powershell', 'Compress-Archive', '-Path', ','.join(source),
                '-DestinationPath', str(target), '-CompressionLevel',
                'NoCompression' if level == 0 else 'Fastest' if level < 5 else 'Optimal',
                '-Force'
            ),
            stdout=stream, stderr=stream
        ).returncode


class ArchivePyZipFile(Archive):

    def unzip(self, source, target, silent=True):
        try:
            zipfile.ZipFile(source).extractall(target)
        except Exception as e:
            if not silent:
                print(e)
            return -1
        return 0

    def zip(self, target, *source, level=5, silent=True):
        try:
            with zipfile.ZipFile(target, 'w',
                                 compression=zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
                all_paths = [
                    p for s in map(Path, source)
                    for p in ([s] if not any(c in s.as_posix() for c in '*?[]')
                              else map(Path, glob.glob(s.as_posix(), recursive=True)))
                ]

                for p in all_paths:
                    if p.is_file():
                        zf.write(p, p.parent.joinpath(p.name))
                    elif p.is_dir():
                        for root, _, files in p.walk():
                            for file in files:
                                zf.write(root.joinpath(file),
                                         root.joinpath(file).relative_to(p.parent))
                                # TODO: decide whether to replicate 7zip's behaviour (./foo vs foo/)
        except Exception as e:
            if not silent:
                print(e)
            return -1
        return 0


class ArchiveZipUnzip(Archive):

    def unzip(self, source, target, silent=True):
        stream = subprocess.DEVNULL if silent else None
        return subprocess.run(
            ('unzip', '-o', str(source), '-d', str(target)),
            stdout=stream, stderr=stream
        ).returncode

    def zip(self, target, *source, level=5, silent=True):
        stream = subprocess.DEVNULL if silent else None
        for src in map(Path, source):
            if src.is_absolute():
                rtcode = subprocess.run(
                    ('zip', '-r', f'-{level}', Path(target).absolute(),
                     src, '-q' if silent else '-v'),
                    stdout=stream, stderr=stream
                ).returncode
            else:
                rtcode = subprocess.run(
                    ('zip', '-r', f'-{level}', Path(target).absolute(),
                     src.name, '-q' if silent else '-v'),
                    cwd=src.parent,
                    stdout=stream, stderr=stream
                ).returncode

            if rtcode == 0:
                continue
        return rtcode
