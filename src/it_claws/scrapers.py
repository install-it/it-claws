import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import lxml.html as lh
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


def resolve_direct_url(_client: Any, url: str, **_: Any) -> str:
    return url


def resolve_static_download(
    client: httpx.Client,
    url: str,
    selector: str,
    attribute: str = "href",
    selector_type: str = "css",
    **_: Any,
) -> str | None:
    response = client.get(url)
    response.raise_for_status()
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
    return urljoin(url, link)


def resolve_intel_static(
    client: httpx.Client,
    url: str,
    **_: Any,
) -> str | None:
    response = client.get(url)
    response.raise_for_status()
    tree = lh.fromstring(response.text)
    node = tree.xpath('//meta[@name="RecommendedDownloadUrl"]')
    if not node:
        return None
    return node[0].get("content")


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


def resolve_msi_dynamic(
    driver: WebDriver, url: str, driver_type: str, driver_name: str
) -> str | None:
    driver.get(url)
    wait = WebDriverWait(driver, 3)

    try:
        wait.until(EC.element_to_be_clickable((By.ID, "ccc-notify-dismiss"))).click()
    except Exception:
        pass

    xpath = f'//div[@class="card card--web"][.//text()[contains(., "{driver_name}")]]//a'
    try:
        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f'//div[@class="badges"]//button[text()="{driver_type}"]',
                )
            )
        ).click()

        return wait.until(EC.presence_of_element_located((By.XPATH, xpath))).get_attribute("href")
    except Exception:
        return None


def resolve_sourceforge_static(
    client: httpx.Client,
    project_name: str,
) -> str | None:
    response = client.get(
        f"https://sourceforge.net/projects/{project_name}/files/",
    )
    response.raise_for_status()
    tree = lh.fromstring(response.text)
    el = tree.xpath('//a[contains(., "Download Latest Version")]')
    if not el:
        return None
    version = el[0].get("title", "").split(":")[0]
    return f"https://download.sourceforge.net/{project_name}{version}"


def resolve_furmark_static(client: httpx.Client, url: str, variant: str = "win64") -> str | None:
    response = client.get(url)
    response.raise_for_status()
    tree = lh.fromstring(response.text)
    xpath = f'//a[contains(., "{variant} - (ZIP)") or contains(., "{variant} - (7ZIP)")]'
    nodes = tree.xpath(xpath)
    if not nodes:
        return None
    show_path = nodes[0].get("href")
    if not show_path:
        return None
    get_path = show_path.replace("/dl/show/", "/dl/get/")
    return f"https://www.geeks3d.com{get_path}"


def resolve_cookies(
    driver: WebDriver, url: str, required_cookies: list[str], timeout: int = 10
) -> dict[str, str]:
    driver.delete_all_cookies()
    driver.get(url)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(1)
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        if all(name in cookies for name in required_cookies):
            return {name: cookies[name] for name in required_cookies}
    raise RuntimeError(f"Required cookies {required_cookies} not set within {timeout}s for {url}")


def download_file(
    client: httpx.Client,
    url: str,
    destination: Path,
    *,
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
) -> Path:
    with client.stream("GET", url, headers=headers, cookies=cookies) as response:
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
                leave=False,
                disable=not sys.stderr.isatty(),
            ) as pbar:
                for chunk in response.iter_bytes():
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
