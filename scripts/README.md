# Automation Scripts

Docker-based automation scripts for headless driver scraping and cloud upload.

## Scripts

| Script | Purpose |
| :--- | :--- |
| `entry_point.sh` | Container entrypoint — sets up config symlinks, then executes the given command. |
| `rclone_upload.sh` | Full pipeline — mounts tmpfs, runs the scraper, creates an archive, uploads via rclone. |

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DOWNLOAD_DIR_NAME` | `downloads` | Name of the temporary staging directory. |
| `ARCHIVE_NAME` | `driver-pack.zip` | File name for the output ZIP archive. |
| `TMPFS` | `1` | Set to `1` to mount a RAM-backed tmpfs volume; `0` to use disk storage. |
| `TMPFS_SIZE` | `24G` | Size of the tmpfs volume (e.g. `24G`, `8G`). |
| `RETRIES` | `1` | Number of in-memory retry attempts per failed download. |
| `COMPRESS_LEVEL` | `5` | 7z compression level (`0`–`9`) for the output ZIP. |
| `RC_REMOTE_PATH` | _(required)_ | rclone remote destination (e.g. `my_remote:bucket/drivers`). |
| `ARGUMENTS` | _(optional)_ | Additional flags passed to `python src/main.py`. |

## Docker Deployment

### Basic run

```bash
docker run --rm --privileged \
  -v /my/host/config:/config \
  -e RC_REMOTE_PATH="onedrive:PC_Deployments" \
  it-claws
```

### Custom compression and retries

```bash
docker run --rm --privileged \
  -v /my/host/config:/config \
  -e RC_REMOTE_PATH="onedrive:PC_Deployments" \
  -e RETRIES="2" \
  -e COMPRESS_LEVEL="9" \
  it-claws
```

> **Note:** The `--privileged` flag is required when `TMPFS=1` to allow the container to mount a RAM disk.

### Overriding the default command

```bash
docker run --name=it-claws \
  -v /path/to/config:/config \
  ghcr.io/install-it/it-claws:latest \
  python src/main.py -t "AMD Chipset Drivers" "Realtek HD Universal Audio"
```
