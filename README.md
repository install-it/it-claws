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
  <a href="https://github.com/install-it/it-claws">
    <img src="https://github.com/user-attachments/assets/83d46686-2893-41c1-9077-ef0fede26dcc" alt="Logo" width="892" height="552">
  </a>

  <h3 align="center">it-claws</h3>

  <p align="center">
    Automated concurrent scraper for staging PC driver deployment environments
    <br />
    <a href="https://github.com/install-it/it-claws/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/install-it/it-claws/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->

## About The Project

it-claws is a Python-based tool that automatically downloads the latest PC hardware drivers, diagnostic tools, and common software from official vendor websites. Using Selenium for browser automation and httpx for static requests, it navigates vendor sites to retrieve up-to-date installation packages — suitable for staging driver packs for enterprise deployment.

Unlike simple download utilities, it-claws runs concurrently with configurable retry logic, supports dynamic and static page scraping, and can pack everything into a compressed ZIP archive via 7z.

The tool serves as a companion to [install-it](https://github.com/install-it/install-it/). See the [Usage](#usage) section for more information.

it-claws also supports **Docker** deployment with tmpfs RAM disk and automated cloud upload via rclone. See [scripts](scripts/) for the automation pipeline.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

[<img src="https://img.shields.io/badge/7zip-000?style=for-the-badge&logo=7zip&logoColor=white">](https://www.7-zip.org/)
[<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Selenium-01a71c?style=for-the-badge&logo=selenium&logoColor=white">](https://www.selenium.dev/)
[<img src="https://img.shields.io/badge/httpx-FF6600?style=for-the-badge&logo=python&logoColor=white">](https://www.python-httpx.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

## Usage

### Basic flow

1. **Select targets**
   - Use `-t` to specify space-separated target names
   - Use `-i` for interactive selection
   - Use `--all` to select all targets
   - Use `--target-from <file>` to load a preset text file

2. **Download**
   - The tool resolves download URLs (static or dynamic)
   - Files are downloaded concurrently with configurable retries

3. **Archive & output**
   - Results are staged in the output directory
   - Optionally pack into a compressed ZIP archive

### Selecting targets

```sh
it-claws -t "AMD Chipset Drivers" "Realtek HD Universal Audio"
it-claws -i
it-claws --all
```

Use a preset file (one target per line, `#` for comments):

```sh
it-claws --target-from presets/default.txt
```

Combine with interactive to tweak the preset before running:

```sh
it-claws --target-from presets/default.txt -i
```

### Output options

```sh
it-claws -o ./my-drivers --max-concurrent 10
```

### Resilience options

```sh
it-claws --max-concurrent 10 --retries 2
```

- `--max-concurrent`: parallel downloads (default: `3`, `1` = sequential)
- `--retries`: retry attempts per failed download (default: `1`)

### Archiving options

```sh
it-claws -o ./downloads -z ./driver-pack.zip --zip-includes ./install-it/conf --compress-level 9
```

- `-z` / `--zip PATH`: destination for the output ZIP archive
- `--zip-includes PATHS [PATHS ...]`: additional files or directories to include in the archive (can be specified multiple times)
- `-l` / `--compress-level`: 7z compression level `0`–`9` (default: `5`)

### How zip entries are determined

7z resolves all paths relative to the current working directory (CWD) at the time of execution. The path you pass to `--zip` and `--zip-includes` determines what gets stored inside the archive:

```sh
# From C:\project, these produce different zip contents:
it-claws -z out.zip --zip-includes ./install-it/conf
# → zip contains: conf/ (all components except last dropped)

it-claws -z out.zip --zip-includes install-it/conf
# → zip contains: install-it/conf/ (full path preserved)

it-claws -z out.zip --zip-includes ./install-it/conf/ install-it/conf/
# → both normalized to: install-it/conf/ (trailing slash stripped)
```

Key path behaviors:
- **`./` drops all components except the last.** `./a/b/c` → `c`, `./a/b` → `b`, `./a` → `a`.
- **`..` alone stores the CWD name.** `..` from `parent\child` → stores as `child`, not `parent`.
- **`..\subdir` works only if `subdir` exists inside the resolved parent directory.**
- **No prefix preserves the full relative path.** `install-it/conf` stores as `install-it/conf`.
- **Trailing `/` is normalized away.** Both `conf/` and `conf` store identically.
- **Paths are relative to your shell's current directory**, not the location of the zip output.
- **Wildcards do not recurse.** `*.ini` only matches files directly in CWD.
- **Duplicate paths cause errors** and non-zero exit — no zip created.
- **Nonexistent paths** cause warnings and non-zero exit — zip is still created but path is skipped.

To include a config directory alongside your downloads in the same archive:

```sh
it-claws -o ./downloads -z ./driver-pack.zip --zip-includes install-it/conf
```

This produces a zip containing both `downloads/` and `install-it/conf/` as top-level entries.

### Extract RAR files on Linux

The `7z` package may not support RAR format. Install `p7zip-full p7zip-rar` as an alternative.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEPLOYMENT -->

## Deployment

This project can be deployed via Docker with tmpfs RAM disk and automated rclone upload. See [`scripts/`](scripts/) for the automation pipeline and environment variable reference.

```bash
docker run --rm --privileged \
  -v /my/host/config:/config \
  -e RC_REMOTE_PATH="onedrive:PC_Deployments" \
  -e RETRIES="2" \
  -e COMPRESS_LEVEL="9" \
  it-claws
```

Override the default command:

```bash
docker run --name=it-claws \
  -v /path/to/config:/config \
  ghcr.io/install-it/it-claws:latest \
  it-claws -t "AMD Chipset Drivers" "Realtek HD Universal Audio"
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [7zip](https://www.7-zip.org/download.html)
- A supported web browser (Chrome, Edge, or Firefox)

### Install dependencies

```bash
uv sync

uv sync --group dev # install dev dependencies
```

### Common commands

**Run the scraper**

```bash
it-claws
```

**Display help**

```bash
it-claws -h
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

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
