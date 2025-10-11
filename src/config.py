"""Configuration module for driver download targets.

This module defines a structured dictionary `CLAW_PRIZES` that categorizes
various hardware-related drivers and utilities into groups such as 'display',
'network', 'miscellaneous', and 'tool'. Each entry specifies metadata for
downloading and optionally renaming driver files, including:

The configuration supports multiple vendors including AMD, Intel, Nvidia,
Realtek, MediaTek, and Qualcomm, and includes utility tools like CrystalDiskInfo,
FurMark, and HWInfo.
"""


import functools

import inquirer

import url
from driver_claw import ClawPrize

CLAW_PRIZES: tuple[ClawPrize] = (
    {
        'group': 'display',
        'path': 'AMD Software\uA789 Adrenalin Edition',
        'url': functools.partial(
                url.amd,
                url='https://www.amd.com/en/support/downloads/drivers.html/graphics/radeon-rx/radeon-rx-9000-series/amd-radeon-rx-9070-xt.html',
                dri_name='win10-win11'),
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'display',
        'path': 'Intel® 7th-10th Gen Processor Graphics',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com/content/www/us/en/download/776137/intel-7th-10th-gen-processor-graphics-windows.html'
        ),
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'display',
        'path': 'Intel® Arc™ & Iris® Xe Graphics',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com/content/www/us/en/download/785597/intel-arc-iris-xe-graphics-windows.html'
        ),
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'display',
        'path': 'GeForce Game Ready Driver',
        'url': functools.partial(url.nvidia_grd, dri_type='desktop'),
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'miscellaneous',
        'path': 'AMD Chipset Drivers',
        'url': functools.partial(
                url.amd,
                url='https://www.amd.com/en/support/downloads/drivers.html/chipsets/am5/x870e.html',
                dri_name='chipset'),
        'file_type': 'exe',
        'rename_as': 'AMD_Chipset_Software'
    },
    {
        'group': 'miscellaneous',
        'path': 'Intel Chipset INF Utility',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com/content/www/us/en/download/19347/chipset-inf-utility.html'
        ),
        'file_type': 'exe',
        'rename_as': None
    },
    {
        'group': 'miscellaneous',
        'path': 'Intel® PPM',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/Motherboard/B860M-AORUS-ELITE-WIFI6E/support#support-dl-driver-wlanbt',
                dri_name='Platform Power Management(PPM)'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_3713_ppm'
    },
    {
        'group': 'miscellaneous',
        'path': 'Intel® Wireless',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com.tw/content/www/us/en/download/19351/intel-wireless-wi-fi-drivers-for-windows-10-and-windows-11.html'
        ),
        'file_type': 'exe',
        'rename_as': 'WiFi-Driver64-Win10-Win11'
    },
    {
        'group': 'miscellaneous',
        'path': 'Intel® Wireless',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com.tw/content/www/us/en/download/18649/intel-wireless-bluetooth-drivers-for-windows-10-and-windows-11.html'
        ),
        'file_type': 'exe',
        'rename_as': 'BT-UWD-Win10-Win11'
    },
    {
        'group': 'miscellaneous',
        'path': 'MediaTek MT7961_79X2\\Bluetooth',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/hk/Motherboard/B850M-FORCE-WIFI6E/support#dl',
                dri_name='MediaTek Wi-Fi 6E Bluetooth Driver'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_4717_mtk6e'
    },
    {
        'group': 'miscellaneous',
        'path': 'MediaTek MT7961_79X2\\WIFI',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/hk/Motherboard/B850M-FORCE-WIFI6E/support#dl',
                dri_name='MediaTek Wi-Fi 6E WIFI Driver'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_4716_mtk6ewifi'
    },
    {
        'group': 'miscellaneous',
        'path': 'MediaTek MT7952_7927\\Bluetooth',
        'url': functools.partial(
                url.gigabyte_wifi_card,
                dri_type='GC-WIFI7 1.1',
                dri_name='Bluetooth'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_2683_mtk'
    },
    {
        'group': 'miscellaneous',
        'path': 'MediaTek MT7952_7927\\WIFI',
        'url': functools.partial(
                url.gigabyte_wifi_card,
                dri_type='GC-WIFI7 1.1',
                dri_name='WIFI'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_2682_mtk'
    },
    {
        'group': 'miscellaneous',
        'path': 'Qualcomm NCM865\\Bluetooth',
        'url': functools.partial(
                url.gigabyte_wifi_card,
                dri_type='GC-WIFI7 1.0',
                dri_name='Bluetooth'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_2687_qualcomm'
    },
    {
        'group': 'miscellaneous',
        'path': 'Qualcomm NCM865\\WIFI',
        'url': functools.partial(
                url.gigabyte_wifi_card,
                dri_type='GC-WIFI7 1.0',
                dri_name='WIFI'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_2686_qualcomm'
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek HD Universal',
        'url': functools.partial(
                url.msi,
                url='https://hk.msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver',
                dri_type='On-Board Audio Drivers',
                dri_name='Realtek HD Universal Driver'
        ),
        'file_type': 'zip/folder',
        'rename_as': None
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8852BE\\Bluetooth',
        'url': 'https://dlcdnets.asus.com/pub/ASUS/mb/02BT/DRV_BT_RTK_8852BE_SZ-TSD_W11_64_V1640132401503_20240924R.zip?model=PRIME%20B650M-A%20WIFI',
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8852BE\\WIFI',
        'url': 'https://dlcdnets.asus.com/pub/ASUS/mb/08WIRELESS/DRV_WiFi_RTK_8852BE_SZ-TSD_W11_64_V6001151240_20220908B.zip?model=PRIME%20B650M-A%20WIFI',
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8852CE\\Bluetooth',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/Motherboard/B860M-AORUS-ELITE-WIFI6E/support#support-dl-driver-wlanbt',
                dri_name='8852 Bluetooth'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_675_realtek8852'
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8852CE\\WIFI',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/Motherboard/B860M-AORUS-ELITE-WIFI6E/support#support-dl-driver-wlanbt',
                dri_name='8852 WIFI'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_674_realtek8852wifi'
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8892AE\\Bluetooth',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/Motherboard/X870-AORUS-ELITE-WIFI7/support#support-dl-driver-wlanbt',
                dri_name='Realtek Bluetooth'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_3702_realtek8922'
    },
    {
        'group': 'miscellaneous',
        'path': 'Realtek RTL8892AE\\WIFI',
        'url': functools.partial(
                url.gigabyte,
                url='https://www.gigabyte.com/Motherboard/X870-AORUS-ELITE-WIFI7/support#support-dl-driver-wlanbt',
                dri_name='Realtek WIFI'
        ),
        'file_type': 'zip/exe',
        'rename_as': 'mb_driver_3701_realtek8922wifi'
    },
    {
        'group': 'network',
        'path': 'Intel® Ethernet Adapter Complete Driver Pack',
        'url': functools.partial(
                url.intel,
                url='https://www.intel.com/content/www/us/en/download/15084/intel-ethernet-adapter-complete-driver-pack.html'
        ),
        'file_type': 'zip',
        'rename_as': None
    },
    {
        'group': 'network',
        'path': 'Realtek PCI-E Ethernet Drivers',
        'url': functools.partial(
                url.msi,
                url='https://hk.msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI/support#driver',
                dri_type='LAN Drivers',
                dri_name='Realtek PCI-E Ethernet Drivers'
        ),
        'file_type': 'zip/folder',
        'rename_as': None
    },
    {
        'group': 'tool',
        'path': 'CrystalDiskinfo',
        'url': functools.partial(url.sourceforge, project_name='crystaldiskinfo'),
        'file_type': 'zip/exe',
        'rename_as': None

    },
    {
        'group': 'tool',
        'path': 'CrystalDiskMark',
        'url': functools.partial(url.sourceforge, project_name='crystalmarkretro'),
        'file_type': 'zip/exe',
        'rename_as': None
    },
    {
        'group': 'tool',
        'path': 'FurMark',
        'url': url.furmark,
        'file_type': 'zip/folder',
        'rename_as': None
    },
    {
        'group': 'tool',
        'path': 'HWInfo',
        'url': url.hwinfo,
        'file_type': 'zip/exe',
        'rename_as': None
    },
    {
        'group': 'tool',
        'path': 'OCCT',
        'url': 'https://www.ocbase.com/download/edition:Personal/os:Windows',
        'file_type': 'exe',
        'rename_as': None
    },
    {
        'group': 'tool',
        'path': 'y-cruncher',
        'url': url.y_cruncher,
        'file_type': 'zip/folder',
        'rename_as': None
    },
    {
        'group': 'software',
        'path': 'Steam',
        'url': 'https://cdn.fastly.steamstatic.com/client/installer/SteamSetup.exe',
        'file_type': 'exe',
        'rename_as': None,
    },
    {
        'group': 'software',
        'path': 'Firefox',
        'url': 'https://download.mozilla.org/?product=firefox-latest-ssl&os=win64',  # &lang=zh-TW
        'file_type': 'exe',
        'rename_as': 'Firefox_Setup.exe',
    },
    {
        'group': 'software',
        'path': 'Discord',
        'url': 'https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64',
        'file_type': 'exe',
        'rename_as': None,
    },
    # {
    #     'group': 'software',
    #     'path': 'Chrome',
    #     'url': 'https://stackoverflow.com/a/65038275; https://nira.com/chrome-offline-installer/',
    #     'file_type': 'exe',
    #     'rename_as': None,
    # },
    # {
    #     'group': 'software',
    #     'path': 'Chrome Enterprise',
    #     'url': 'https://stackoverflow.com/a/75754456',
    #     'file_type': 'exe',
    #     'rename_as': None,
    # },
    {
        'group': 'software',
        'path': 'VLC Player',
        'url': functools.partial(url.vlc, architecture='win64-win64'),
        'file_type': 'exe',
        'rename_as': 'vlc-win64',
    },
    {
        'group': 'software',
        'path': 'NordVPN',
        'url': 'https://downloads.nordcdn.com/apps/windows/NordVPN/latest/NordVPNSetup.exe',
        'file_type': 'exe',
        'rename_as': None,
    },
    {
        'group': 'software',
        'path': 'Surfshark',
        'url': 'https://downloads.surfshark.com/windows/latest/SurfsharkSetup.exe',
        'file_type': 'exe',
        'rename_as': None,
    },
    {
        'group': 'software',
        'path': '7zip',
        'url': functools.partial(url.sourceforge, project_name='sevenzip'),
        'file_type': 'exe',
        'rename_as': '7zip_Setup.exe',
    },
    {
        'group': 'software',
        'path': 'Spotify',
        'url': 'https://download.scdn.co/SpotifySetup.exe',
        'file_type': 'exe',
        'rename_as': None,
    },
    {
        'group': 'software',
        'path': 'iTunes',
        'url': 'https://www.apple.com/itunes/download/win64',
        'file_type': 'exe',
        'rename_as': None,
    },
)
