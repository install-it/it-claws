# it-claws
<a id="readme-top"></a>


<!-- PROJECT SHIELDS -->
<div align="center">

  [![Tag][tag-shield]][tag-url]
  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![License][license-shield]][license-url]
  
</div>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">it-claws</h3>

  <p align="center">
    A common-line tool that automates the process of find and download the latest common hardware drivers, and diagnostic tool.
    <br />
    <a href="https://github.com/install-it/it-claws/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/install-it/it-claws/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

it-claws is a Python-based command-line utility for downloading the latest PC hardware drivers and diagnostic tools. Leveraging Selenium, it automatically navigates official websites and motherboard manufacturers' pages to locate and retrieve the most up-to-date versions of essential drivers and utilities.

This tool also serves as a companion to [install-it](https://github.com/install-it/install-it/). Refer to the [Usage](#including-extra-files-in-the-archive) section for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With
[<img src="https://img.shields.io/badge/python-306998?style=for-the-badge&logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/selenium-01a71c?style=for-the-badge&logo=selenium&logoColor=white">](https://www.selenium.dev/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- [Python](https://www.python.org/downloads/) >= 3.12
- [7zip](https://www.7-zip.org/download.html) (Optional)

### Setup

#### Install dependencies
```sh
pip install -r requirements.txt
```

### Commands

- Run the script
  ```sh
  python src/main.py
  ```

- Display help message
  ```sh
  python src/main.py -h
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

###  Specify 7-Zip Executable Location

it-claws uses 7-Zip to extract and compress files.
By default, it-claws will look for the 7-Zip executable under `bin/7zip`, which will be included in release builds.

If you are not comfortable with that, you can remove the `bin` folder. it-claws will then look for 7-Zip that is installed in the system. <br />
If 7-Zip is not available, `PowerShell` will be used as a fall back. Please note that:

- Compression level will be lower compared to 7-Zip.
- There could be a higher chance of failure when extracting certain downloaded archives (only support `.zip`).

### Customise Crawl Configurations

The default crawl configuration is located in `src/config.py`, which includes a curated list of common hardware drivers and diagnostic tools.
To use a custom configuration file, specify it with the `-c` or `--claw-config` option. The tool accepts both JSON and Python source files.

The module `src/url.py` provides helper methods to extract download URLs from well-known hardware manufacturers and vendors. You can leverage these utilities when drafting your own claw configuration.

#### Python pickle file

The expected type is ```dict[str, Iterable[ClawPrize]]```.

```sh
python src/main.py -c ./custom-config.pkl
```

#### Python source file

When using a Python file, it-claws will look for a variable named `CLAW_CONFIG` defined in the specified source.
The expected type is ```dict[str, Iterable[ClawPrize]]```.

```sh
python src/main.py -c ./custom-config.py
```

#### JSON file

Refer to the [JSON Schema](https://raw.githubusercontent.com/install-it/it-claws/main/claw-config-schema.json) for guidance on constructing a valid claw configuration.

```sh
python src/main.py -c ./custom-config.json
```

###  Including Extra Files in the Archive

Use `-i` or `--include-files` to specify the file or directory paths you want to include in the output archive.
To include multiple paths, either separate them with spaces or provide the option multiple times.

```sh
python src/main.py -i foo/ bar/ -i README.md
```

The `conf/` directory contains configuration files for the default set of drivers and tools used by driver-box.
To use this tool to download drivers and utilities for driver-box, include the directory as input:

```sh
python src/main.py -i conf/
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[tag-url]: https://github.com/install-it/it-claws/releases
[tag-shield]: https://img.shields.io/github/v/tag/install-it/it-claws?style=for-the-badge&label=LATEST&color=%23B1B1B1
[contributors-shield]: https://img.shields.io/github/contributors/install-it/it-claws.svg?style=for-the-badge
[contributors-url]: https://github.com/install-it/it-claws/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/install-it/it-claws.svg?style=for-the-badge
[forks-url]: https://github.com/install-it/it-claws/network/members
[stars-shield]: https://img.shields.io/github/stars/install-it/it-claws.svg?style=for-the-badge
[stars-url]: https://github.com/install-it/it-claws/stargazers
[issues-shield]: https://img.shields.io/github/issues/install-it/it-claws.svg?style=for-the-badge
[issues-url]: https://github.com/install-it/it-claws/issues
[license-shield]: https://img.shields.io/github/license/install-it/it-claws.svg?style=for-the-badge
[license-url]: https://github.com/install-it/it-claws/blob/master/LICENSE.txt
