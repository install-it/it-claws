import asyncio
import logging
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from selectolax.parser import HTMLParser
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


async def resolve_static_download(
    client: httpx.AsyncClient,
    url: str,
    selector: str,
    attribute: str = "href",
    **_: Any,
) -> str | None:
    response = await client.get(url)
    response.raise_for_status()

    node = HTMLParser(response.text).css_first(selector)
    if node is None:
        logger.warning("Static selector '%s' matched nothing on %s", selector, url)
        return None

    link = node.attributes.get(attribute)
    if not link:
        logger.warning("Attribute '%s' not found on matched node at %s", attribute, url)
        return None

    if link.startswith("//"):
        return f"https:{link}"
    if link.startswith("/"):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{link}"
    return link


def resolve_dynamic_download(
    driver: WebDriver,
    url: str,
    xpath: str,
    attribute: str = "href",
    scroll_to_load: bool = False,
    **_: Any,
) -> str | None:
    driver.get(url)

    if scroll_to_load:
        try:
            driver.execute_script(
                "window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })"
            )
            time.sleep(2)
        except Exception as exc:
            logger.error("Scroll execution failed on %s: %s", url, exc)

    try:
        value = driver.find_element("xpath", xpath).get_attribute(attribute)
        if not value:
            logger.warning("Dynamic attribute '%s' not found via xpath on %s", attribute, url)
            return None
        return value
    except Exception as exc:
        logger.error("Dynamic resolution failed on %s: %s", url, exc)
        return None


async def download_file(
    client: httpx.AsyncClient,
    url: str,
    destination: Path,
    semaphore: asyncio.Semaphore | None = None,
) -> Path:
    cm = semaphore if semaphore else asyncio.nullcontext()
    async with cm:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                raise RuntimeError(f"Expected binary content but received HTML from {url}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

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
                raise RuntimeError(f"No .exe found inside archive {zip_path}")

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
                raise RuntimeError(
                    f"Unexpected archive structure in {zip_path}: multiple top-level items"
                )

    zip_path.unlink(missing_ok=True)
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
