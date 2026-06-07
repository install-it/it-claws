import asyncio
import logging
import subprocess
from pathlib import Path

import httpx
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .models import DownloadJob
from .scrapers import (
    cleanup_empty_directories,
    download_file,
    extract_installer_from_zip,
    extract_sfx,
    resolve_static_download,
)

logger = logging.getLogger(__name__)


class ConcurrentPipeline:
    def __init__(
        self,
        max_downloads: int = 5,
        retries: int = 1,
        compress_level: int = 5,
    ) -> None:
        self._semaphore = asyncio.Semaphore(max_downloads)
        self._driver_lock = asyncio.Lock()
        self._results: list[tuple[DownloadJob, bool, str]] = []
        self._retries = retries
        self._compress_level = compress_level

    async def run(
        self,
        jobs: list[DownloadJob],
        output_root: Path,
        archive_path: Path | None = None,
    ) -> list[tuple[DownloadJob, bool, str]]:
        output_root.mkdir(parents=True, exist_ok=True)

        driver = None
        if any(j.target.resolver_type == "dynamic" for j in jobs):
            driver = await asyncio.to_thread(self._create_driver)

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                tasks = [self._process_job(job, client, driver) for job in jobs]
                await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            if driver:
                await asyncio.to_thread(driver.quit)

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
            logger.info("Archive created: %s", archive_path)

        return self._results

    async def _process_job(
        self,
        job: DownloadJob,
        client: httpx.AsyncClient,
        driver: webdriver.Chrome | None,
    ) -> None:
        try:
            job.destination_directory.mkdir(parents=True, exist_ok=True)

            if job.target.resolver_type == "static":
                download_url = await resolve_static_download(
                    client,
                    **job.target.resolver_kwargs,
                )
            elif job.target.resolver_type == "dynamic":
                if driver is None:
                    raise RuntimeError("Dynamic resolver requested but no driver available")
                async with self._driver_lock:
                    download_url = await asyncio.to_thread(
                        job.target.resolver,
                        driver,
                        **job.target.resolver_kwargs,
                    )
            else:
                raise RuntimeError(f"Unknown resolver type: {job.target.resolver_type}")

            if not download_url:
                raise RuntimeError(f"Failed to resolve download URL for {job.target.name}")

            for attempt in range(self._retries + 1):
                try:
                    if job.target.file_type == "exe":
                        name = job.target.rename_as or download_url.split("/")[-1]
                        dest = job.destination_directory / f"{name}.exe"
                        await download_file(client, download_url, dest, self._semaphore)
                    elif job.target.file_type in ("zip", "zip/exe", "zip/folder"):
                        zip_path = job.destination_directory / download_url.split("/")[-1]
                        await download_file(client, download_url, zip_path, self._semaphore)
                        await asyncio.to_thread(
                            extract_installer_from_zip,
                            zip_path,
                            job.destination_directory,
                            job.target.file_type,
                            job.target.rename_as,
                        )
                    elif job.target.file_type == "sfx":
                        sfx_path = job.destination_directory / download_url.split("/")[-1]
                        await download_file(client, download_url, sfx_path, self._semaphore)
                        await asyncio.to_thread(
                            extract_sfx,
                            sfx_path,
                            job.destination_directory,
                            job.target.rename_as,
                        )
                    else:
                        raise RuntimeError(f"Unsupported file type: {job.target.file_type}")
                    break
                except Exception:
                    if attempt < self._retries:
                        logger.warning(
                            "Retry %d/%d for %s", attempt + 1, self._retries, job.target.name
                        )
                        await asyncio.sleep(5)
                    else:
                        raise

            self._results.append((job, True, f"Successfully downloaded {job.target.name}"))
            logger.info("Completed: %s", job.target.name)

        except Exception as exc:
            error_msg = f"Failed {job.target.name}: {exc}"
            logger.error(error_msg)
            self._results.append((job, False, error_msg))

    @staticmethod
    def _create_driver() -> webdriver.Chrome:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={UserAgent().random}")
        return webdriver.Chrome(options=options)
