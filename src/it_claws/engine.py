import asyncio
import subprocess
from pathlib import Path

import httpx
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from tqdm import tqdm

from .models import DownloadJob
from .scrapers import (
    cleanup_empty_directories,
    download_file,
    extract_installer_from_zip,
    extract_sfx,
    resolve_cookies,
)


class ConcurrentPipeline:
    def __init__(
        self,
        max_downloads: int = 5,
        retries: int = 1,
        compress_level: int = 5,
    ) -> None:
        self._semaphore = asyncio.Semaphore(max_downloads)
        self._driver_lock = asyncio.Lock()
        self._driver: webdriver.Firefox | None = None
        self._results: list[tuple[DownloadJob, bool, str]] = []
        self._retries = retries
        self._compress_level = compress_level

    async def run(
        self,
        jobs: list[DownloadJob],
        output_root: Path,
        archive_path: Path | None = None,
        *,
        user_agent: str | None = None,
    ) -> list[tuple[DownloadJob, bool, str]]:
        output_root.mkdir(parents=True, exist_ok=True)

        self._user_agent = user_agent

        try:
            tasks = [self._process_job(job, i) for i, job in enumerate(jobs)]
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self._destroy_driver()

        cleanup_empty_directories(output_root)

        if archive_path and not any(not s for _, s, _ in self._results):
            await asyncio.to_thread(
                subprocess.run,
                [
                    "7z",
                    "a",
                    "-tzip",
                    f"-mx={self._compress_level}",
                    str(archive_path),
                    f"{output_root}/*",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            tqdm.write(f"Archive created: {archive_path}")

        return self._results

    async def _process_job(
        self,
        job: DownloadJob,
        position: int = 0,
    ) -> None:
        try:
            job.destination_directory.mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=120.0,
                headers={"User-Agent": self._user_agent}
                if job.target.random_ua and self._user_agent
                else None,
            ) as client:
                if job.target.include_cookies is None:
                    if job.target.resolver_type == "static":
                        download_url = await job.target.resolver(
                            client,
                            **job.target.resolver_kwargs,
                        )
                    elif job.target.resolver_type == "dynamic":
                        driver = await self._ensure_driver()
                        async with self._driver_lock:
                            download_url = await asyncio.to_thread(
                                job.target.resolver,
                                driver,
                                **job.target.resolver_kwargs,
                            )
                    if not download_url:
                        raise RuntimeError(f"Failed to resolve download URL for {job.target.name}")
                else:
                    download_url = None

                headers = job.target.request_headers

                for attempt in range(self._retries + 1):
                    try:
                        if job.target.include_cookies is not None:
                            driver = await self._ensure_driver()
                            async with self._driver_lock:
                                download_url = await asyncio.to_thread(
                                    job.target.resolver,
                                    driver,
                                    **job.target.resolver_kwargs,
                                )
                                if not download_url:
                                    raise RuntimeError(
                                        f"Failed to resolve download URL for {job.target.name}"
                                    )
                                cookies = await asyncio.to_thread(
                                    resolve_cookies,
                                    driver,
                                    download_url,
                                    job.target.include_cookies,
                                )

                        if not download_url:
                            raise RuntimeError(
                                f"Failed to resolve download URL for {job.target.name}"
                            )

                        if job.target.file_type == "exe":
                            name = job.target.rename_as or download_url.split("/")[-1].split("?")[0]
                            if not name.lower().endswith(".exe") and "." not in name:
                                name += ".exe"
                            dest = job.destination_directory / name
                        elif job.target.file_type in ("zip", "zip/exe", "zip/folder", "sfx"):
                            fname = download_url.split("/")[-1].split("?")[0]
                            dest = job.destination_directory / fname
                        else:
                            raise RuntimeError(f"Unsupported file type: {job.target.file_type}")

                        dl_cookies = cookies if job.target.include_cookies is not None else None
                        await download_file(
                            client,
                            download_url,
                            dest,
                            self._semaphore,
                            position=position,
                            headers=headers,
                            cookies=dl_cookies,
                        )

                        if job.target.file_type in ("zip", "zip/exe", "zip/folder"):
                            await asyncio.to_thread(
                                extract_installer_from_zip,
                                dest,
                                job.destination_directory,
                                job.target.file_type,
                                job.target.rename_as,
                            )
                        elif job.target.file_type == "sfx":
                            await asyncio.to_thread(
                                extract_sfx,
                                dest,
                                job.destination_directory,
                                job.target.rename_as,
                            )

                        break
                    except Exception:
                        if attempt < self._retries:
                            tqdm.write(f"Retry {attempt + 1}/{self._retries} for {job.target.name}")
                            await asyncio.sleep(5)
                        else:
                            raise

                self._results.append((job, True, f"Successfully downloaded {job.target.name}"))
                tqdm.write(f"Completed {job.target.name}")

        except Exception as exc:
            error_msg = f"Failed {job.target.name}: {exc}"
            tqdm.write(error_msg)
            self._results.append((job, False, error_msg))

    async def _ensure_driver(self) -> webdriver.Firefox:
        if self._driver is not None:
            return self._driver
        async with self._driver_lock:
            if self._driver is not None:
                return self._driver
            self._driver = await asyncio.to_thread(self._create_driver, self._user_agent)
        return self._driver

    def _destroy_driver(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    @staticmethod
    def _create_driver(user_agent: str | None = None) -> webdriver.Firefox:
        options = FirefoxOptions()
        options.add_argument("--headless")
        if user_agent:
            profile = FirefoxProfile()
            profile.set_preference("general.useragent.override", user_agent)
            options.profile = profile
        return webdriver.Firefox(options=options)
