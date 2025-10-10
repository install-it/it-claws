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

<p align="center">
  <img src="https://github.com/user-attachments/assets/83d46686-2893-41c1-9077-ef0fede26dcc" width="892" height="552">
</p>

it-claws is a Python-based command-line tool for downloading the latest PC hardware drivers, diagnostic tools and more. Leveraging Selenium, it is able to automatically navigate official websites to locate and retrieve the most up-to-date versions of the target software.

This tool also serves as a companion to [install-it](https://github.com/install-it/install-it/). Refer to the [Usage](#including-extra-files-in-the-archive) section for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

[<img src="https://img.shields.io/badge/7zip-000?style=for-the-badge&logo=7zip&logoColor=white">](https://www.7-zip.org/)
[<img src="https://img.shields.io/badge/python-306998?style=for-the-badge&logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/selenium-01a71c?style=for-the-badge&logo=selenium&logoColor=white">](https://www.selenium.dev/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- [Python](https://www.python.org/downloads/) >= 3.12
- [7zip](https://www.7-zip.org/download.html)
- [Google Chrome](https://www.google.com/chrome/), [Microsoft Edge](https://www.microsoft.com/en-us/edge/download), or [Mozilla Firefox](https://www.firefox.com/en-US/)

### Setup

#### Install Python Dependencies
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

### Customising Scraping Configurations

#### Creating configuration

it-claws comes with a brunch of software scraping preset (see: [`src/config.py`](https://github.com/install-it/it-claws/blob/main/src/config.py)), which includes a curated list of common hardware drivers, diagnostic tools and common software.

Run the following command to configure your scraping list:

```sh
python src/main.py --configure
```

#### Providing your custom configuration

To use a custom configuration file, specify it with the `-c` or `--claw-config` option.

The module [`src/url.py`](https://github.com/install-it/it-claws/blob/main/src/url.py) provides helper methods to extract download URLs from various websites. You can leverage those when drafting your own scraping configuration.

it-claw accepts Python pickle files, Python source files, and JSON files. Details are as follow.

#### Python Pickle File

The expected type is `Iterable[ClawPrize]`.

```sh
python src/main.py -c ./custom-config.pkl
```

#### Python Source File

it-claws will look for the `CLAW_CONFIG` variable defined in the specified `.py` file.

```python
# custom-config.py

CLAW_CONFIG: Iterable[ClawPrize] = [
  # define your configuration here
]
```

```sh
python src/main.py -c ./custom-config.py
```

#### JSON File

Refer to the [JSON Schema](https://raw.githubusercontent.com/install-it/it-claws/main/claw-config-schema.json) for guidance on constructing a valid scraping configuration.

```sh
python src/main.py -c ./custom-config.json
```

### Specific the Browser for Scraping

it-claws required a web browser to scrape the download URL. You can use any one of Google Chrome, Microsoft Edge, or Mozilla Firefox (default).

To specific a browser, use `-w` or `--web-driver` with the name of the browser choice. 

```sh
python src/main.py -w Chrome
```

###  Including Extra Files in the Archive

Use `-i` or `--include-files` to specify the file(s) or directory path(s) you want to include in the output archive.
To include multiple paths, either separate them with spaces or provide the option multiple times.

```sh
python src/main.py -i foo/ bar/ -i README.md
```

The `install-it/conf` directory contains configuration files of the scraping preset for [install-it](https://github.com/install-it/install-it).
To use this tool to download drivers and utilities for install-it, include the directory:

```sh
python src/main.py -i ./install-it/conf
```

Then, you can import the output archive into install-it using its import function.

### Extract RAR Files in Linux

`7z` or the binaries from [7-zip.org](https://www.7-zip.org/download.html) does not seem to support RAR format.

To extract RAR files, consider to use the package `p7zip-full p7zip-rar` instead of `7z`.

### Docker Deployment

it-claws provided container images for you to run it in containerised enviroments.
Get the docker image details at [Packages](https://github.com/install-it/it-claws/pkgs/container/it-claws).

```sh
docker run -d \
  --name=it-claws \
  -v /path/to/rclone-config:/config/rclone \
  -v /path/to/config:/config/app \
  -v /path/to/downloads:/app/downloads \ # optional
  ghcr.io/install-it/it-claws:latest
```

A few scripts for automation are provided. See [scripts](https://github.com/install-it/it-claws/tree/main/scripts) for more information.

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
