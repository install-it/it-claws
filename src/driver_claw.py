"""Driver clawing and download automation module.
"""

import contextlib
import functools
import glob
import importlib.util
import json
import os
import pickle
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Callable, Iterable, Literal, TypedDict
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.webdriver import Remote
from tqdm import tqdm

from archive import Archive


@contextlib.contextmanager
def get_browser():
    options = webdriver.FirefoxOptions()
    # options.set_preference('intl.accept_languages', 'zh-Hant')
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)

    try:
        yield driver
    finally:
        driver.quit()


class ClawPrize(TypedDict):
    path: str
    """Local file path where the downloaded or extracted file will be stored."""
    url: str | Callable[[Remote], str]
    """URL to download the file, or a callable that generates the URL from a Remote object."""
    file_type: Literal['exe', 'zip', 'zip/folder', 'zip/exe']
    """Type of the downloaded file, used to determine how it should be handled."""
    rename_as: str | None
    """Optional new name for the executable after download or extraction."""


class DriverClaw:

    file_error_log = '.failedclaws.pkl'

    dest: Path
    """Directory to save downloaded files.
    """

    archive: Archive

    @classmethod
    def from_file(cls, archive: Archive, prizes_path: Path, destination: Path) -> 'DriverClaw':
        if '.json' == prizes_path.suffix:
            with open(prizes_path) as f:
                return cls(archive, json.load(f), destination)
        elif '.pkl' == prizes_path.suffix:
            with open(prizes_path, 'rb') as f:
                return cls(archive, pickle.load(f), destination)
        elif '.py' == prizes_path.suffix:
            spec = importlib.util.spec_from_file_location(
                'custom_config', prizes_path)
            custom = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom)
            return cls(archive, custom.CLAW_PRIZES, destination)
        raise ValueError(f'\'{prizes_path}\' is not a supported file format')

    @classmethod
    def from_failed(cls, archive: Archive, destination: Path) -> 'DriverClaw':
        return cls.from_file(archive, Path(cls.file_error_log).joinpath(cls.file_error_log), destination)

    def __init__(self, archive: Archive, prizes: dict[str, Iterable[ClawPrize]], destination: str | Path):
        self.archive = archive
        self.prizes = prizes
        self.dest = Path(destination)

    def start(self, on_error: Literal['exit', 'log', 'ignore']) -> dict[str, list[ClawPrize]]:
        """Start downloading drivers based on provided targets.

        Args:
            on_error (Literal['exit', 'log', 'ignore']): Error handling mode.

        Returns:
            dict[str, list[ClawPrize]]: Dictionary of failed downloads claw configurations by category.
        """
        failed: dict[str, list[ClawPrize]] = {}

        with get_browser() as browser:
            claw_items = [{**item, 'category': category}
                          for category, items in self.prizes.items()
                          for item in items]

            for i, item in enumerate(claw_items):
                category = item['category']
                fullpath = self.dest.joinpath(category, item['path'])
                fullpath.mkdir(parents=True, exist_ok=True)

                try:
                    print(f'Processing {i+1:>2}/{len(claw_items)}: '
                          f'[{category}] {item['path']}')

                    print('├ Locating download URL...')
                    url = (item['url']
                           if type(item['url']) is str
                           else item['url'](browser))

                    print('├ Downloading...')
                    self.download_and_save(
                        url, item['file_type'], item['rename_as'], fullpath)
                except Exception as e:
                    print(f'┴ Failed: {e}')

                    if on_error == 'exit':
                        sys.exit(1)
                    if on_error == 'log':
                        failed.setdefault(category, [])
                        failed[category].append(item)
                    continue

                print('┴ Completed.')

        if on_error == 'log' and len(failed) > 0:
            self._dump_failed(failed)

        if len(failed) == 0:
            self.dest.joinpath(self.file_error_log).unlink(True)

        return failed

    def download_and_save(self, url: str, file_type: Literal['exe', 'zip', 'zip/exe', 'zip/folder'], rename_as: str | None,  path: str | Path) -> None:
        """Download and save a file from a URL, organizing it based on file type.

        Args:
            url (str): Download URL.
            file_type (Literal["exe", "zip", "zip/exe", "zip/folder"]): Type of file.
            rename_as (str | None): Optional rename for the file.
            path (str | Path): Destination path for the file.

        Raises:
            ValueError: If the response is an HTML page.
            RuntimeError: If zip extraction fails.
            NotImplementedError: If multiple executables are found in zip/exe.
        """
        path = Path(path)
        headers = {} if 'sourceforge' in url or 'geeks3d' in url else {
            'referer': urlparse(url).hostname,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0'
        }

        with requests.get(url, stream=True, headers=headers, allow_redirects=True) as resp:
            resp.raise_for_status()
            if 'html' in resp.headers['content-type']:
                raise ValueError('Received an HTML page instead of a file.')

            resp.raw.read = functools.partial(
                resp.raw.read, decode_content=True)

            with tempfile.TemporaryFile(delete_on_close=False, suffix='.zip' if 'zip' in file_type else None) as temp:
                with tqdm.wrapattr(resp.raw, 'read', total=int(resp.headers.get('Content-Length', 0))) as content:
                    shutil.copyfileobj(content, temp)
                temp.close()

                print('├ Organizing downloaded file...')
                if 'zip' in file_type:
                    if (self.archive.unzip(temp.name, path) != 0):
                        raise RuntimeError('Failed to extract zip file.')

                    if file_type == 'zip/folder':
                        for directory in os.listdir(path):
                            for file in glob.glob('*', root_dir=path.joinpath(directory)):
                                shutil.move(
                                    path.joinpath(directory, file), path)
                            shutil.rmtree(path.joinpath(directory))

                    if rename_as:
                        if len(exe := glob.glob(str(path.joinpath('*.exe')))) > 1:
                            raise NotImplementedError(
                                'Multiple executables found in zip.')
                        shutil.move(exe[0], path.joinpath(f'{rename_as}.exe'))
                else:
                    fname = (re.findall('filename=(.+)', resp.headers['Content-Disposition'])[0]
                             if 'Content-Disposition' in resp.headers
                             else urlparse(url).path.split('/')[-1])
                    if rename_as:
                        fname = f'{rename_as}.{fname.split('.')[-1]}'
                    shutil.move(temp.name, path.joinpath(fname.strip('\"')))

    def _dump_failed(self, failed: dict[str, list[ClawPrize]]):
        """Save failed downloads to the error log.
        """
        with open(self.dest.joinpath(self.file_error_log), 'wb') as f:
            return pickle.dump(failed, f)
