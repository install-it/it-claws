from .models import ScrapeTarget
from .scrapers import (
    resolve_direct_url,
    resolve_furmark_dynamic,
    resolve_gigabyte_dynamic,
    resolve_intel_dynamic,
    resolve_msi_dynamic,
    resolve_nvidia_grd,
    resolve_static_download,
    resolve_y_cruncher_dynamic,
)

HARDWARE_CATALOG: list[ScrapeTarget] = [
    ScrapeTarget(
        name="AMD Software Software - Adrenalin Edition",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.amd.com/en/support/downloads/drivers.html/graphics/radeon-rx/radeon-rx-9000-series/amd-radeon-rx-9070-xt.html",
            "selector": 'a[href*="win11-"][href$=".exe"]',
        },
        file_type="exe",
        request_headers={"referer": "https://www.amd.com"},
        default_folder="display",
    ),
    ScrapeTarget(
        name="Intel 7th-10th Gen Processor Graphics",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/776137/intel-7th-10th-gen-processor-graphics-windows.html"
        },
        file_type="zip",
        default_folder="display",
    ),
    ScrapeTarget(
        name="Intel 11th-14th Gen Processor Graphics",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/864990/intel-11th-14th-gen-processor-graphics-windows.html"
        },
        file_type="zip",
        default_folder="display",
    ),
    ScrapeTarget(
        name="Intel Arc & Iris Xe Graphics",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html"
        },
        file_type="zip",
        default_folder="display",
    ),
    ScrapeTarget(
        name="GeForce Game Ready Driver",
        resolver_type="dynamic",
        resolver=resolve_nvidia_grd,
        resolver_kwargs={"url": "https://www.nvidia.com/zh-tw/geforce/game-ready-drivers/"},
        file_type="exe",
        default_folder="display",
    ),
    ScrapeTarget(
        name="AMD Chipset Drivers",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.amd.com/en/support/downloads/drivers.html/chipsets/am5/x870e.html",
            "selector": 'a[href*="chipset"][href$=".exe"]',
        },
        file_type="exe",
        rename_as="AMD_Chipset_Software",
        request_headers={"referer": "https://www.amd.com"},
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Intel Chipset INF Utility",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/19347/chipset-inf-utility.html"
        },
        file_type="exe",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Intel Wireless Wi-Fi",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/19351/intel-wireless-wi-fi-drivers-for-windows-10-and-windows-11.html"
        },
        file_type="exe",
        rename_as="WiFi-Driver64-Win10-Win11",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Intel Wireless Bluetooth",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/18649/intel-wireless-bluetooth-drivers-for-windows-10-and-windows-11.html"
        },
        file_type="exe",
        rename_as="BT-UWD-Win10-Win11",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="MediaTek MT7961_79X2 Bluetooth",
        resolver_type="dynamic",
        resolver=resolve_gigabyte_dynamic,
        resolver_kwargs={
            "url": "https://www.gigabyte.com/hk/Motherboard/B850M-FORCE-WIFI6E-rev-10/support",
            "driver_name": "MediaTek Wi-Fi 6E Bluetooth Driver",
        },
        file_type="zip/exe",
        rename_as="mb_driver_4717_mtk6e",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="MediaTek MT7961_79X2 WIFI",
        resolver_type="dynamic",
        resolver=resolve_gigabyte_dynamic,
        resolver_kwargs={
            "url": "https://www.gigabyte.com/hk/Motherboard/B850M-FORCE-WIFI6E-rev-10/support",
            "driver_name": "MediaTek Wi-Fi 6E WIFI Driver",
        },
        file_type="zip/exe",
        rename_as="mb_driver_4716_mtk6ewifi",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Realtek HD Universal Audio",
        resolver_type="dynamic",
        resolver=resolve_msi_dynamic,
        resolver_kwargs={
            "url": "https://hk.msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver",
            "driver_type": "On-Board Audio Drivers",
            "driver_name": "Realtek HD Universal Driver",
        },
        file_type="zip/folder",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Realtek RTL8852BE Bluetooth",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://dlcdnets.asus.com/pub/ASUS/mb/02BT/DRV_BT_RTK_8852BE_SZ-TSD_W11_64_V1640132401503_20240924R.zip?model=PRIME%20B650M-A%20WIFI"
        },
        file_type="zip",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Realtek RTL8852BE WIFI",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://dlcdnets.asus.com/pub/ASUS/mb/08WIRELESS/DRV_WiFi_RTK_8852BE_SZ-TSD_W11_64_V6001151240_20220908B.zip?model=PRIME%20B650M-A%20WIFI"
        },
        file_type="zip",
        default_folder="miscellaneous",
    ),
    ScrapeTarget(
        name="Intel Ethernet Complete Driver Pack",
        resolver_type="dynamic",
        resolver=resolve_intel_dynamic,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/15084/intel-ethernet-adapter-complete-driver-pack.html"
        },
        file_type="zip",
        default_folder="network",
    ),
    ScrapeTarget(
        name="Realtek PCI-E Ethernet Drivers",
        resolver_type="dynamic",
        resolver=resolve_msi_dynamic,
        resolver_kwargs={
            "url": "https://hk.msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver",
            "driver_type": "LAN Drivers",
            "driver_name": "Realtek PCI-E Ethernet Drivers",
        },
        file_type="zip/folder",
        default_folder="network",
    ),
]

UTILITY_CATALOG: list[ScrapeTarget] = [
    ScrapeTarget(
        name="CrystalDiskInfo",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://sourceforge.net/projects/crystaldiskinfo/files/",
            "selector": 'a[title*="Download Latest Version"]',
        },
        file_type="zip/exe",
        default_folder="tool",
    ),
    ScrapeTarget(
        name="CrystalDiskMark",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://sourceforge.net/projects/crystalmarkretro/files/",
            "selector": 'a[title*="Download Latest Version"]',
        },
        file_type="zip/exe",
        default_folder="tool",
    ),
    ScrapeTarget(
        name="FurMark",
        resolver_type="dynamic",
        resolver=resolve_furmark_dynamic,
        resolver_kwargs={
            "url": "https://www.geeks3d.com/furmark/downloads/",
            "variant": "win64",
        },
        file_type="zip/folder",
        default_folder="tool",
    ),
    ScrapeTarget(
        name="HWInfo",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://sourceforge.net/projects/hwinfo/files/",
            "selector": 'a[title*="Download Latest Version"]',
        },
        file_type="zip/exe",
        default_folder="tool",
    ),
    ScrapeTarget(
        name="OCCT",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://www.ocbase.com/download/edition:Personal/os:Windows"},
        file_type="exe",
        default_folder="tool",
    ),
    ScrapeTarget(
        name="y-cruncher",
        resolver_type="dynamic",
        resolver=resolve_y_cruncher_dynamic,
        resolver_kwargs={
            "url": "https://www.numberworld.org/y-cruncher/#Download",
            "variant": "Windows",
        },
        file_type="zip/folder",
        default_folder="tool",
    ),
]

SOFTWARE_CATALOG: list[ScrapeTarget] = [
    ScrapeTarget(
        name="Steam",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://cdn.fastly.steamstatic.com/client/installer/SteamSetup.exe"
        },
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Firefox",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64"
        },
        file_type="exe",
        rename_as="Firefox_Setup",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Discord",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64"
        },
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="VLC Player",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://download.videolan.org/pub/videolan/vlc/last/win64/",
            "selector": 'a[href$="-win64.exe"]',
        },
        file_type="exe",
        rename_as="vlc-win64",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Surfshark",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://downloads.surfshark.com/windows/latest/SurfsharkSetup.exe"
        },
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="7-Zip",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://sourceforge.net/projects/sevenzip/files/",
            "selector": 'a[title*="Download Latest Version"]',
        },
        file_type="exe",
        rename_as="7zip_Setup",
        default_folder="software",
    ),
    ScrapeTarget(
        name="iTunes",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://www.apple.com/itunes/download/win64"},
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Zoom Workplace",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://zoom.us/client/latest/ZoomInstallerFull.msi?archType=x64"},
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="GitHub Desktop",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://central.github.com/deployments/desktop/desktop/latest/win32"
        },
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Miniconda",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        },
        file_type="exe",
        default_folder="software",
    ),
    ScrapeTarget(
        name="Visual Studio Code",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
        },
        file_type="exe",
        rename_as="VSCodeUserSetup-x64",
        default_folder="software",
    ),
]

ALL_TARGETS: list[ScrapeTarget] = [*HARDWARE_CATALOG, *UTILITY_CATALOG, *SOFTWARE_CATALOG]


def get_target_by_name(name: str) -> ScrapeTarget | None:
    for target in ALL_TARGETS:
        if target.name == name:
            return target
    return None


def get_target_names() -> list[str]:
    return [t.name for t in ALL_TARGETS]
