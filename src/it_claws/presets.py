from dataclasses import replace

from .models import ScrapeTarget, TargetGroup
from .scrapers import (
    resolve_direct_url,
    resolve_furmark_static,
    resolve_gigabyte_dynamic,
    resolve_intel_static,
    resolve_msi_dynamic,
    resolve_nvidia_grd,
    resolve_sourceforge_static,
    resolve_static_download,
)

TARGETS: list[ScrapeTarget | TargetGroup] = [
    ScrapeTarget(
        name="AMD Software - Adrenalin Edition",
        path="display/{name}",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.amd.com/en/support/downloads/drivers.html/graphics/radeon-rx/radeon-rx-9000-series/amd-radeon-rx-9070-xt.html",
            "selector": 'a[href*="win11-"][href$=".exe"]',
        },
        file_type="exe",
        request_headers={"referer": "https://www.amd.com"},
        rename_as="whql-amd-software-adrenalin-edition-win11-b",
    ),
    ScrapeTarget(
        name="Intel 7th-10th Gen Processor Graphics",
        path="display/Intel® 7th-10th Gen Processor Graphics",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/776137/intel-7th-10th-gen-processor-graphics-windows.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="sfx",
    ),
    ScrapeTarget(
        name="Intel 11th-14th Gen Processor Graphics",
        path="display/Intel® 11th-14th Gen Processor Graphics",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/864990/intel-11th-14th-gen-processor-graphics-windows.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="sfx",
    ),
    ScrapeTarget(
        name="Intel Arc & Iris Xe Graphics",
        path="display/Intel® Arc™ & Iris® Xe Graphics",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="sfx",
    ),
    ScrapeTarget(
        name="GeForce Game Ready Driver",
        path="display/{name}",
        resolver_type="dynamic",
        resolver=resolve_nvidia_grd,
        resolver_kwargs={"url": "https://www.nvidia.com/zh-tw/geforce/game-ready-drivers/"},
        file_type="exe",
        rename_as="desktop-win10-win11-64bit-international-dch-whql",
    ),
    ScrapeTarget(
        name="AMD Chipset Drivers",
        path="miscellaneous/{name}",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.amd.com/en/support/downloads/drivers.html/chipsets/am5/x870e.html",
            "selector": 'a[href*="chipset"][href$=".exe"]',
        },
        file_type="exe",
        rename_as="AMD_Chipset_Software",
        request_headers={"referer": "https://www.amd.com"},
    ),
    ScrapeTarget(
        name="Intel Chipset INF Utility",
        path="miscellaneous/{name}",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/19347/chipset-inf-utility.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="exe",
    ),
    TargetGroup(
        name="Intel Wireless",
        path="miscellaneous/Intel® Wireless",
        members=[
            ScrapeTarget(
                name="Wi-Fi",
                path="{name}",
                resolver_type="static",
                resolver=resolve_intel_static,
                resolver_kwargs={
                    "url": "https://www.intel.com/content/www/us/en/download/19351/intel-wireless-wi-fi-drivers-for-windows-10-and-windows-11.html"
                },
                random_ua=False,
                include_cookies=["aws-waf-token"],
                file_type="exe",
                rename_as="WiFi-Driver64-Win10-Win11",
            ),
            ScrapeTarget(
                name="Bluetooth",
                path="{name}",
                resolver_type="static",
                resolver=resolve_intel_static,
                resolver_kwargs={
                    "url": "https://www.intel.com/content/www/us/en/download/18649/intel-wireless-bluetooth-drivers-for-windows-10-and-windows-11.html"
                },
                random_ua=False,
                include_cookies=["aws-waf-token"],
                file_type="exe",
                rename_as="BT-UWD-Win10-Win11",
            ),
        ],
    ),
    TargetGroup(
        name="MediaTek MT7961_79X2",
        path="miscellaneous/{name}",
        members=[
            ScrapeTarget(
                name="Bluetooth",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/B850M-FORCE-WIFI6E-rev-10/support",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "MediaTek Wi-Fi 6E Bluetooth Driver")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_4717_mtk6e",
            ),
            ScrapeTarget(
                name="WIFI",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/B850M-FORCE-WIFI6E-rev-10/support",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "MediaTek Wi-Fi 6E WIFI Driver")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_4716_mtk6ewifi",
            ),
        ],
    ),
    ScrapeTarget(
        name="Realtek HD Universal",
        path="miscellaneous/{name}",
        resolver_type="dynamic",
        resolver=resolve_msi_dynamic,
        resolver_kwargs={
            "url": "https://msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver",
            "driver_type": "On-Board Audio Drivers",
            "driver_name": "Realtek HD Universal Driver",
        },
        file_type="zip/folder",
    ),
    TargetGroup(
        name="Realtek RTL8852BE",
        path="miscellaneous/{name}",
        members=[
            ScrapeTarget(
                name="Bluetooth",
                path="{name}",
                resolver_type="static",
                resolver=resolve_direct_url,
                resolver_kwargs={
                    "url": "https://dlcdnets.asus.com/pub/ASUS/mb/02BT/DRV_BT_RTK_8852BE_SZ-TSD_W11_64_V1640132401503_20240924R.zip?model=PRIME%20B650M-A%20WIFI"
                },
                file_type="zip",
            ),
            ScrapeTarget(
                name="WIFI",
                path="{name}",
                resolver_type="static",
                resolver=resolve_direct_url,
                resolver_kwargs={
                    "url": "https://dlcdnets.asus.com/pub/ASUS/mb/08WIRELESS/DRV_WiFi_RTK_8852BE_SZ-TSD_W11_64_V6001151240_20220908B.zip?model=PRIME%20B650M-A%20WIFI"
                },
                file_type="zip",
            ),
        ],
    ),
    TargetGroup(
        name="Realtek RTL8852CE",
        path="miscellaneous/{name}",
        members=[
            ScrapeTarget(
                name="Bluetooth",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/B860M-AORUS-ELITE-WIFI6E/support#support-dl-driver-wlanbt",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "8852 Bluetooth")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_675_realtek8852",
            ),
            ScrapeTarget(
                name="WIFI",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/B860M-AORUS-ELITE-WIFI6E/support#support-dl-driver-wlanbt",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "8852 WIFI")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_674_realtek8852wifi",
            ),
        ],
    ),
    TargetGroup(
        name="Realtek RTL8892AE",
        path="miscellaneous/{name}",
        members=[
            ScrapeTarget(
                name="Bluetooth",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/X870-AORUS-ELITE-WIFI7-rev-10-11/support",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "Realtek Bluetooth")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_3702_realtek8922",
            ),
            ScrapeTarget(
                name="WIFI",
                path="{name}",
                resolver_type="dynamic",
                resolver=resolve_gigabyte_dynamic,
                resolver_kwargs={
                    "url": "https://www.gigabyte.com/Motherboard/X870-AORUS-ELITE-WIFI7-rev-10-11/support",
                    "selector": (
                        '//tr[contains(@class, "item-group")]'
                        '[.//text()[contains(., "Realtek WIFI")]][1]//a'
                    ),
                },
                file_type="zip/exe",
                rename_as="mb_driver_3701_realtek8922wifi",
            ),
        ],
    ),
    ScrapeTarget(
        name="Intel Platform Performance Package",
        path="miscellaneous/Intel® Platform Performance Package",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/869519/intel-platform-performance-package.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="exe",
    ),
    ScrapeTarget(
        name="Intel Ethernet Adapter Complete Driver Pack",
        path="network/Intel® Ethernet Adapter Complete Driver Pack",
        resolver_type="static",
        resolver=resolve_intel_static,
        resolver_kwargs={
            "url": "https://www.intel.com/content/www/us/en/download/15084/intel-ethernet-adapter-complete-driver-pack.html"
        },
        random_ua=False,
        include_cookies=["aws-waf-token"],
        file_type="zip",
    ),
    ScrapeTarget(
        name="Realtek PCI-E Ethernet Drivers",
        path="network/{name}",
        resolver_type="dynamic",
        resolver=resolve_msi_dynamic,
        resolver_kwargs={
            "url": "https://msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver",
            "driver_type": "LAN Drivers",
            "driver_name": "Realtek PCI-E Ethernet Drivers",
        },
        file_type="zip/folder",
    ),
    ScrapeTarget(
        name="CrystalDiskInfo",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_sourceforge_static,
        resolver_kwargs={"project_name": "crystaldiskinfo"},
        file_type="zip/exe",
        random_ua=False,
    ),
    ScrapeTarget(
        name="CrystalDiskMark",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_sourceforge_static,
        resolver_kwargs={"project_name": "crystalmarkretro"},
        file_type="zip/exe",
        random_ua=False,
    ),
    ScrapeTarget(
        name="FurMark",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_furmark_static,
        resolver_kwargs={
            "url": "https://www.geeks3d.com/furmark/downloads/",
            "variant": "win64",
        },
        file_type="zip/folder",
    ),
    ScrapeTarget(
        name="HWInfo",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_sourceforge_static,
        resolver_kwargs={"project_name": "hwinfo"},
        file_type="zip/exe",
        random_ua=False,
    ),
    ScrapeTarget(
        name="OCCT",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://www.ocbase.com/download/edition:Personal/os:Windows"},
        file_type="exe",
    ),
    ScrapeTarget(
        name="y-cruncher",
        path="tool/{name}",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://www.numberworld.org/y-cruncher/#Download",
            "selector": '//table[contains(., "Download Link")]//tr[contains(., "Windows")]//a',
            "selector_type": "xpath",
        },
        file_type="zip/folder",
    ),
    ScrapeTarget(
        name="Steam",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://cdn.fastly.steamstatic.com/client/installer/SteamSetup.exe"
        },
        file_type="exe",
    ),
    ScrapeTarget(
        name="Firefox",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64"
        },
        file_type="exe",
        rename_as="Firefox_Setup",
    ),
    ScrapeTarget(
        name="Discord",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64"
        },
        file_type="exe",
    ),
    ScrapeTarget(
        name="VLC Player",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_static_download,
        resolver_kwargs={
            "url": "https://download.videolan.org/pub/videolan/vlc/last/win64/",
            "selector": 'a[href$="-win64.exe"]',
        },
        file_type="exe",
        rename_as="vlc-win64",
    ),
    ScrapeTarget(
        name="Surfshark",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://downloads.surfshark.com/windows/latest/SurfsharkSetup.exe"
        },
        file_type="exe",
    ),
    ScrapeTarget(
        name="7zip",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_sourceforge_static,
        resolver_kwargs={"project_name": "sevenzip"},
        file_type="exe",
        rename_as="7zip_Setup",
        random_ua=False,
    ),
    ScrapeTarget(
        name="iTunes",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://www.apple.com/itunes/download/win64"},
        file_type="exe",
    ),
    ScrapeTarget(
        name="Zoom Workplace",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={"url": "https://zoom.us/client/latest/ZoomInstallerFull.msi?archType=x64"},
        file_type="exe",
    ),
    ScrapeTarget(
        name="Github Desktop",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://central.github.com/deployments/desktop/desktop/latest/win32"
        },
        file_type="exe",
    ),
    ScrapeTarget(
        name="Miniconda",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        },
        file_type="exe",
    ),
    ScrapeTarget(
        name="Visual Studio Code",
        path="software/{name}",
        resolver_type="static",
        resolver=resolve_direct_url,
        resolver_kwargs={
            "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
        },
        file_type="exe",
        rename_as="VSCodeUserSetup-x64",
    ),
]


def get_target_by_name(name: str) -> ScrapeTarget | None:
    for t in TARGETS:
        if isinstance(t, ScrapeTarget) and t.name == name:
            return t
        if isinstance(t, TargetGroup):
            for m in t.members:
                if m.name == name:
                    return m
    return None


def get_selection_choices() -> list[str]:
    return [t.name for t in TARGETS]


def expand_selection(names: list[str]) -> list[ScrapeTarget]:
    group_map = {t.name: t for t in TARGETS if isinstance(t, TargetGroup)}
    result: list[ScrapeTarget] = []
    for name in names:
        if name in group_map:
            group = group_map[name]
            group_path = group.path.format(name=group.name)
            for member in group.members:
                full_path = f"{group_path}/{member.path}"
                result.append(replace(member, path=full_path))
        else:
            target = next(
                (t for t in TARGETS if isinstance(t, ScrapeTarget) and t.name == name), None
            )
            if target:
                result.append(target)
    return result
