from .models import ScrapeTarget
from .scrapers import resolve_dynamic_download, resolve_static_download

HARDWARE_CATALOG: list[ScrapeTarget] = [
    ScrapeTarget(
        name="NVIDIA GeForce Drivers",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.nvidia.com/Download/index.aspx",
            "selector": "a.download-btn",
        },
        file_type="exe",
        default_folder="gpu",
    ),
    ScrapeTarget(
        name="AMD Radeon Drivers",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.amd.com/en/support",
            "selector": "a[href*='drivers']",
        },
        file_type="exe",
        default_folder="gpu",
    ),
    ScrapeTarget(
        name="Intel Graphics Drivers",
        resolver_type="dynamic",
        resolver=resolve_dynamic_download,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download-center/home.html",
            "xpath": '//a[contains(@href, ".exe")]',
            "scroll_to_load": True,
        },
        file_type="exe",
        default_folder="gpu",
    ),
    ScrapeTarget(
        name="Realtek Audio Drivers",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.realtek.com/en/component/zoo/category/pc-audio-codecs-high-definition-audio-codecs-software",
            "selector": "a[href*='.zip']",
        },
        file_type="zip/exe",
        default_folder="audio",
    ),
    ScrapeTarget(
        name="Intel LAN Drivers",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download-center/home.html",
            "selector": "a[href*='network'][href*='.exe']",
        },
        file_type="exe",
        default_folder="network",
    ),
]

UTILITY_CATALOG: list[ScrapeTarget] = [
    ScrapeTarget(
        name="7-Zip",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.7-zip.org/download.html",
            "selector": "a[href*='x64.exe']",
        },
        file_type="exe",
        rename_as="7zip-setup",
        default_folder="utilities",
    ),
    ScrapeTarget(
        name="HWiNFO",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.hwinfo.com/download/",
            "selector": "a[href*='.exe']",
        },
        file_type="zip/exe",
        rename_as="hwinfo-setup",
        default_folder="utilities",
    ),
]

ALL_TARGETS: list[ScrapeTarget] = [*HARDWARE_CATALOG, *UTILITY_CATALOG]


def get_target_by_name(name: str) -> ScrapeTarget | None:
    for target in ALL_TARGETS:
        if target.name == name:
            return target
    return None


def get_target_names() -> list[str]:
    return [t.name for t in ALL_TARGETS]
