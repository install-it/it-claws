import os
import queue
import subprocess
import sys
import threading
from concurrent.futures import Future, as_completed
from pathlib import Path

import httpx
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from tqdm import tqdm

from .models import DownloadJob
from .sevenz import find_7z
from .scrapers import (
    cleanup_empty_directories,
    download_file,
    extract_installer_from_zip,
    extract_sfx,
    resolve_cookies,
)


class DaemonThreadPool:
    def __init__(self, max_workers: int) -> None:
        self._work_queue: queue.Queue = queue.Queue()
        self._futures: list[Future] = []
        self._shutdown = False
        self._threads = [
            threading.Thread(target=self._worker_loop, daemon=True) for _ in range(max_workers)
        ]
        for t in self._threads:
            t.start()

    def submit(self, fn, /, *args, **kwargs) -> Future:
        future: Future = Future()
        self._work_queue.put((fn, args, kwargs, future))
        self._futures.append(future)
        return future

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False) -> None:
        self._shutdown = True
        if cancel_futures:
            while True:
                try:
                    _, _, _, future = self._work_queue.get_nowait()
                except queue.Empty:
                    break
                future.cancel()
        for _ in self._threads:
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()

    def __enter__(self) -> "DaemonThreadPool":
        return self

    def __exit__(self, *args) -> None:
        self.shutdown(wait=False)

    def _worker_loop(self) -> None:
        while not self._shutdown:
            try:
                item = self._work_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                break
            fn, args, kwargs, future = item
            if future.cancelled():
                continue
            try:
                future.set_result(fn(*args, **kwargs))
            except BaseException as e:
                future.set_exception(e)


class ConcurrentPipeline:
    def __init__(
        self,
        max_concurrent: int = 3,
        retries: int = 1,
        compress_level: int = 5,
    ) -> None:
        self._max_concurrent = max_concurrent
        self._retries = retries
        self._compress_level = compress_level
        self._driver_lock = threading.Lock()
        self._driver: WebDriver | None = None
        self._results: list[tuple[DownloadJob, bool, str]] = []
        self._user_agent: str | None = None

    def execute(
        self,
        jobs: list[DownloadJob],
        output_root: Path,
        archive_path: Path | None = None,
        archive_include: list[str] | None = None,
    ) -> list[tuple[DownloadJob, bool, str]]:
        output_root.mkdir(parents=True, exist_ok=True)
        self._user_agent = UserAgent().chrome
        self._results.clear()

        pending = list(jobs)
        succeeded: list = []
        remaining_retries = self._retries

        while pending:
            scraped: list = []
            for job in pending:
                job.destination_directory.mkdir(parents=True, exist_ok=True)
                try:
                    download_url, headers = self._scrape(job)
                    dest = self._build_dest_path(job, download_url)
                    scraped.append((job, download_url, dest, headers))
                except Exception as exc:
                    tqdm.write(f"Failed to resolve {job.target.name}: {exc}")

            if scraped:
                with DaemonThreadPool(max_workers=self._max_concurrent) as pool:
                    futures: dict[Future, DownloadJob] = {
                        pool.submit(self._download_job, *entry): entry[0] for entry in scraped
                    }

                    try:
                        for future in as_completed(futures):
                            job = futures[future]
                            try:
                                future.result()
                                succeeded.append(job)
                                self._results.append(
                                    (job, True, f"Successfully downloaded {job.target.name}")
                                )
                                tqdm.write(f"Completed {job.target.name}")
                            except Exception as exc:
                                tqdm.write(f"Failed {job.target.name}: {exc}")
                    except KeyboardInterrupt:
                        pool.shutdown(wait=False, cancel_futures=True)
                        self._destroy_driver()
                        sys.exit(1)

            pending = [j for j in pending if j not in succeeded]
            if pending and remaining_retries > 0:
                remaining_retries -= 1
                self._destroy_driver()
                tqdm.write(
                    f"Retrying {len(pending)} failed job(s)... ({remaining_retries} retries left)"
                )
            elif pending:
                for job in pending:
                    self._results.append(
                        (job, False, f"Failed {job.target.name}: retries exhausted")
                    )
                break

        self._destroy_driver()
        cleanup_empty_directories(output_root)

        if archive_path and all(s for _, s, _ in self._results):
            args = [
                find_7z(), "a", "-tzip", f"-mx={self._compress_level}",
                str(archive_path), str(output_root),
            ]
            if archive_include:
                args.extend(archive_include)
            subprocess.run(args, capture_output=True, text=True, check=True)
            tqdm.write(f"Archive created: {archive_path}")

        return self._results

    def _scrape(self, job: DownloadJob) -> tuple[str, dict[str, str] | None]:
        if job.target.resolver_type == "static":
            with httpx.Client(
                follow_redirects=True,
                timeout=120.0,
                headers={"User-Agent": self._user_agent}
                if job.target.random_ua and self._user_agent
                else None,
            ) as client:
                download_url = job.target.resolver(
                    client,
                    **job.target.resolver_kwargs,
                )
        elif job.target.resolver_type == "dynamic":
            driver = self._ensure_driver()
            download_url = job.target.resolver(
                driver,
                **job.target.resolver_kwargs,
            )
        else:
            raise RuntimeError(f"Unknown resolver type: {job.target.resolver_type}")

        if not download_url:
            raise RuntimeError(f"Failed to resolve download URL for {job.target.name}")

        return download_url, job.target.request_headers

    def _build_dest_path(self, job: DownloadJob, download_url: str) -> Path:
        if job.target.file_type == "exe":
            name = job.target.rename_as or download_url.split("/")[-1].split("?")[0]
            if not name.lower().endswith(".exe") and "." not in name:
                name += ".exe"
            return job.destination_directory / name

        if job.target.file_type in ("zip", "zip/exe", "zip/folder", "sfx"):
            fname = download_url.split("/")[-1].split("?")[0]
            return job.destination_directory / fname

        raise RuntimeError(f"Unsupported file type: {job.target.file_type}")

    def _download_job(
        self,
        job: DownloadJob,
        download_url: str,
        dest: Path,
        headers: dict[str, str] | None,
    ) -> None:
        cookies = None
        if job.target.include_cookies is not None:
            with self._driver_lock:
                driver = self._ensure_driver()
                cookies = resolve_cookies(driver, download_url, job.target.include_cookies)

        with httpx.Client(
            follow_redirects=True,
            timeout=120.0,
            headers={"User-Agent": self._user_agent}
            if job.target.random_ua and self._user_agent
            else None,
        ) as client:
            download_file(
                client,
                download_url,
                dest,
                headers=headers,
                cookies=cookies,
            )

        if job.target.file_type in ("zip", "zip/exe", "zip/folder"):
            extract_installer_from_zip(
                dest,
                job.destination_directory,
                job.target.file_type,
                job.target.rename_as,
            )
        elif job.target.file_type == "sfx":
            extract_sfx(dest, job.destination_directory, job.target.rename_as)

    def _ensure_driver(self) -> WebDriver:
        if self._driver is not None:
            return self._driver
        self._driver = self._create_driver()
        return self._driver

    def _destroy_driver(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    def _create_driver(self) -> WebDriver:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")

        if os.environ.get("CHROME_NO_SANDBOX", "").lower() in ("1", "true", "yes", "y"):
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        options.add_experimental_option(
            "prefs",
            {
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
            },
        )
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        if self._user_agent:
            options.add_argument(f"--user-agent={self._user_agent}")

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "deny"})
        return driver
