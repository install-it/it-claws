"""Handling archive operations.
"""

import os
import subprocess
from abc import ABC
from pathlib import Path


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

    path_7zip: Path

    def __init__(self, path_7zip: str | Path | None):
        super().__init__()

        self.path_7zip = Path(path_7zip)
        if not self.path_7zip.exists():
            raise FileNotFoundError(f'cannot locate {self.path_7zip}')

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
             " ".join(source), f'-mx{level}'),
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
