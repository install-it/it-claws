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
import tempfile
from pathlib import Path
from typing import Callable, Literal, TypedDict
from urllib.parse import urlparse

import requests
from fake_useragent import FakeUserAgent
from selenium import webdriver
from selenium.webdriver import Remote
from tqdm import tqdm

from archive import Archive

SupportedWebDriver = Literal['Chrome', 'Edge', 'Firefix']


class ClawPrize(TypedDict):
    group: str
    """category or group name for organizing downloaded files."""
    path: str
    """path to store downloaded or extracted files"""
    url: str | Callable[[Remote], str]
    """URL to download the file, or a callable that generates the URL from a Remote object."""
    file_type: Literal['exe', 'zip', 'zip/folder', 'zip/exe']
    """Type of the downloaded file, used to determine how it should be handled."""
    rename_as: str | None
    """optional new name for the executable after download or extraction."""


class DriverClaw:

    dest: Path
    """Directory to save downloaded files.
    """

    archive: Archive

    driver_name: SupportedWebDriver

    @classmethod
    def from_file(cls, archive: Archive, driver_name: SupportedWebDriver, prizes_path: Path, destination: Path) -> 'DriverClaw':
        if '.json' == prizes_path.suffix:
            with open(prizes_path) as f:
                return cls(archive=archive, driver_name=driver_name,
                           prizes=json.load(f), destination=destination)
        elif '.pkl' == prizes_path.suffix:
            with open(prizes_path, 'rb') as f:
                return cls(archive=archive, driver_name=driver_name,
                           prizes=pickle.load(f), destination=destination)
        elif '.py' == prizes_path.suffix:
            spec = (importlib
                    .util
                    .spec_from_file_location('custom_config', prizes_path))
            spec.loader.exec_module(
                custom := importlib.util.module_from_spec(spec))
            return cls(archive=archive, driver_name=driver_name,
                       prizes=custom.CLAW_PRIZES, destination=destination)
        raise ValueError(f'\'{prizes_path}\' is not a supported file format')

    def __init__(self, archive: Archive, driver_name: SupportedWebDriver,
                 prizes: list[ClawPrize], destination: str | Path):
        self.archive = archive
        self.driver_name = driver_name
        self.prizes = prizes
        self.dest = Path(destination)

    def start(self, stop_on_error: bool) -> list[ClawPrize]:
        """Start downloading drivers based on provided targets.

        Args:
            stop_on_error (bool): Error handling mode.

        Returns:
            list[ClawPrize]: List of failed downloads claw configurations.
        """
        failed: list['ClawPrize'] = []
        with self._get_browser() as driver:
            for i, prize in enumerate(self.prizes):
                fullpath = self.dest.joinpath(prize['group'], prize['path'])
                fullpath.mkdir(parents=True, exist_ok=True)

                try:
                    print(f'Processing {i+1:>2}/{len(self.prizes)}: '
                          f'[{prize['group']}] {prize['path']}')

                    print('├ Locating download URL...')
                    url = (prize['url']
                           if type(prize['url']) is str
                           else prize['url'](driver))

                    print('├ Downloading...')
                    self.download_and_save(
                        url, prize['file_type'], prize['rename_as'], fullpath)
                except Exception as e:
                    print(f'┴ Failed: {e}')

                    if stop_on_error:
                        return

                    failed.append(prize)
                    continue
                print('┴ Completed.')
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
        headers = ({}
                   if any(s in url for s in ('asus', 'sourceforge', 'geeks3d'))
                   else {'referer': urlparse(url).hostname})

        with requests.get(url, stream=True, headers=headers, allow_redirects=True) as resp:
            resp.raise_for_status()
            if 'html' in resp.headers['content-type']:
                raise ValueError('Received an HTML page instead of a file.')

            resp.raw.read = functools.partial(
                resp.raw.read, decode_content=True)

            with tempfile.NamedTemporaryFile(delete_on_close=False, suffix='.zip' if 'zip' in file_type else None) as temp:
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

    @contextlib.contextmanager
    def _get_browser(self):
        options = webdriver.__dict__[f'{self.driver_name}Options']()
        user_agent = FakeUserAgent(
            browsers=[self.driver_name], platforms='desktop').random

        if self.driver_name == 'Firefox':
            options.add_argument('--headless')
            options.set_preference('general.useragent.override', user_agent)
        else:
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--user-agent={user_agent}')

        driver: webdriver.Remote = (webdriver.
                                    __dict__[self.driver_name](options=options))

        try:
            yield driver
        finally:
            driver.quit()
