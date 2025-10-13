# Docker Script Manual

## entry_point.sh

Serves as the Docker image entry point, not intended for overriding `CMD`.

Configures symbolic links for volume-mapped configuration files.
Avoid modifying unless familiar with the image's internal mechanics.

## rclone_upload.sh

Automates file downloads, archiving, and rclone-based uploads with retry logic and optional tmpfs mounting.

### Usage

#### Environment Variables

| Variable            | Description                            | Default           |
|--------------------|----------------------------------------|-------------------|
| `DOWNLOAD_DIR_NAME`| Download directory name                | `downloads`       |
| `ARCHIVE_NAME`     | Output zip file name                   | `driver-pack.zip` |
| `MAX_RETRIES`      | Retry attempts for download failures   | `3`               |
| `RETRY_DELAY`      | Seconds between retries                | `10`              |
| `TMPFS`            | Enable tmpfs mount (1: enabled, 0: disabled) | `1`         |
| `TMPFS_SIZE`       | tmpfs mount size                       | `24G`             |
| `RC_REMOTE_PATH`   | rclone remote upload path (required)   |                   |
| `ARGUMENTS`        | Extra arguments for `main.py`          |                   |

#### Exit Codes

| Code 	| Meaning             	|
|------	|---------------------	|
| 0    	| Success             	|
| 16   	| rclone failure      	|
| 32   	| tmpfs mount failure 	|


### Workflow

1. Mounts tmpfs at `/app/downloads` if `TMPFS=1`. <br />
   The tmpfs will be used to storing downloaded files and the result archive.
2. Runs it-claws. <br />
   Retries up to `MAX_RETRIES` times on scraping failure, waiting `RETRY_DELAY` seconds.
3. Syncs archive to `RC_REMOTE_PATH` using rclone.

### Notes

- Requires preconfigured rclone with valid `RC_REMOTE_PATH`.
- Set `TMPFS_SIZE` based on available memory to prevent mount errors.

> [!IMPORTANT]  
> `--privileged` must be passed if tmpfs mount is enabled.