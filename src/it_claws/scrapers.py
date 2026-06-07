import asyncio
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import lxml.html as lh
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from tqdm import tqdm


async def resolve_direct_url(client: Any, url: str, **_: Any) -> str:
    return url


async def resolve_static_download(
    client: httpx.AsyncClient,
    url: str,
    selector: str,
    attribute: str = "href",
    selector_type: str = "css",
    **_: Any,
) -> str | None:
    response = await client.get(url)
    response.raise_for_status()

    print(response.text)
    tree = lh.fromstring(response.text)
    if selector_type == "xpath":
        nodes = tree.xpath(selector)
    else:
        nodes = tree.cssselect(selector)
    if not nodes:
        return None
    link = nodes[0].get(attribute)
    if not link:
        return None
    if link.startswith("//"):
        return f"https:{link}"
    if link.startswith("/"):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{link}"
    return link


def resolve_intel_dynamic(driver: WebDriver, url: str) -> str | None:
    driver.get(url)
    try:
        return driver.find_element(
            By.CSS_SELECTOR, "button.dc-page-available-downloads-hero-button__cta"
        ).get_attribute("data-href")
    except Exception:
        return None


def resolve_nvidia_grd(driver: WebDriver, url: str) -> str | None:
    driver.get(url)
    try:
        landing_url = driver.find_element(By.XPATH, '//a[@id="DsktpGrdDwnldBtn"]').get_attribute(
            "href"
        )
        driver.get(landing_url)
        return driver.find_element(By.XPATH, '//a[contains(@id, "agreeDownload")]').get_attribute(
            "href"
        )
    except Exception:
        return None


def resolve_gigabyte_dynamic(driver: WebDriver, url: str, driver_name: str) -> str | None:
    driver.get(url)
    time.sleep(2)
    try:
        xpath = (
            f'//tr[contains(@class, "item-group")][.//text()[contains(., "{driver_name}")]][1]//a'
        )
        return driver.find_element(By.XPATH, xpath).get_attribute("href")
    except Exception:
        return None


def resolve_msi_dynamic(
    driver: WebDriver, url: str, driver_type: str, driver_name: str
) -> str | None:
    driver.get(url)
    try:
        time.sleep(1)
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight / 3 })")
        time.sleep(1)
    except Exception:
        pass
    try:
        driver.find_element(
            By.XPATH, f'//div[@class="badges"]//button[text()="{driver_type}"]'
        ).click()
        time.sleep(0.5)
        xpath = f'//div[@class="card card--web"][.//text()[contains(., "{driver_name}")]]//a'
        return driver.find_element(By.XPATH, xpath).get_attribute("href")
    except Exception:
        return None


def resolve_furmark_dynamic(driver: WebDriver, url: str, variant: str) -> str | None:
    driver.get(url)
    try:
        xpath = f'//a[contains(., "{variant} - (ZIP)") or contains(., "{variant} - (7ZIP)")]'
        landing_url = driver.find_element(By.XPATH, xpath).get_attribute("href")
        driver.get(landing_url)
        time.sleep(5)
        return driver.find_element(By.XPATH, '//a[contains(., "Geeks3D server")]').get_attribute(
            "href"
        )
    except Exception:
        return None


def resolve_y_cruncher_dynamic(driver: WebDriver, url: str, variant: str) -> str | None:
    driver.get(url)
    try:
        xpath = f'//table[contains(., "Download Link")]//tr[contains(., "{variant}")]//a'
        return driver.find_element(By.XPATH, xpath).get_attribute("href")
    except Exception:
        return None


async def download_file(
    client: httpx.AsyncClient,
    url: str,
    destination: Path,
    semaphore: asyncio.Semaphore | None = None,
    *,
    position: int = 0,
    headers: dict[str, str] | None = None,
) -> Path:
    async with semaphore or asyncio.nullcontext():
        async with client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()
            if "text/html" in response.headers.get("content-type", ""):
                raise RuntimeError(f"Expected binary stream but received HTML from {url}")
            total = int(response.headers.get("content-length", 0))
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "wb") as f:
                with tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=destination.name,
                    position=position,
                    leave=False,
                    disable=not sys.stderr.isatty(),
                ) as pbar:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                        pbar.update(len(chunk))
    return destination


def extract_installer_from_zip(
    zip_path: Path,
    target_dir: Path,
    file_type: str,
    rename_as: str | None = None,
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)

        if file_type in ("zip/exe", "zip/folder"):
            exe_files = list(tmp_path.rglob("*.exe"))
            if not exe_files:
                raise RuntimeError(f"No execution binary discovered inside zip archive {zip_path}")
            installer = exe_files[0]
            shutil.move(
                str(installer),
                str(target_dir / (f"{rename_as}.exe" if rename_as else installer.name)),
            )
        else:
            extracted = list(tmp_path.iterdir())
            if len(extracted) == 1 and extracted[0].is_file():
                src = extracted[0]
                shutil.move(
                    str(src),
                    str(target_dir / (f"{rename_as}{src.suffix}" if rename_as else src.name)),
                )
            else:
                raise RuntimeError(f"Unexpected compound structure inside zip archive {zip_path}")
    zip_path.unlink(missing_ok=True)
    return target_dir


def extract_sfx(
    sfx_path: Path,
    target_dir: Path,
    rename_as: str | None = None,
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            ["7z", "x", str(sfx_path), f"-o{tmp_path}", "-y"],
            capture_output=True,
            text=True,
            check=True,
        )
        exe_files = list(tmp_path.rglob("*.exe"))
        if not exe_files:
            raise RuntimeError(f"No executable found in SFX archive {sfx_path}")
        installer = exe_files[0]
        shutil.move(
            str(installer),
            str(target_dir / (f"{rename_as}.exe" if rename_as else installer.name)),
        )
    sfx_path.unlink(missing_ok=True)
    return target_dir


def cleanup_empty_directories(root: Path) -> None:
    for dirpath, dirnames, filenames in sorted(
        root.walk(top_down=False), key=lambda x: str(x[0]), reverse=True
    ):
        if not dirnames and not filenames and dirpath != root:
            try:
                dirpath.rmdir()
            except OSError:
                pass
