# Docker Script Manual

## entry_point.sh

Docker image entry point, not intended for overriding `CMD`.

Configures symbolic links for volume-mapped configuration files.
Avoid modifying unless familiar with the image's internal mechanics.

## rclone_upload.sh

Automates file downloads, archiving, and rclone uploads with retries and optional tmpfs.

### Usage

#### Environment Variables

| Variable            | Description                            | Default           |
|--------------------|----------------------------------------|-------------------|
| `DOWNLOAD_DIR_NAME`| Download directory name                | `downloads`       |
| `ARCHIVE_NAME`     | Output zip file name                   | `driver-pack.zip` |
| `MAX_TRIES`        | Number of attempts for download        | `3`               |
| `RETRY_DELAY`      | Seconds between retries                | `10`              |
| `TMPFS`            | Enable tmpfs mount (1: on, 0: off)     | `1`               |
| `TMPFS_SIZE`       | tmpfs mount size                       | `24G`             |
| `KEEP_DOWNLOADS`   | Keep downloads after archiving (1: on, 0: off) | `1`     |
| `RC_REMOTE_PATH`   | rclone remote upload path (required)   |                   |
| `ARGUMENTS`        | Extra arguments for `main.py`          |                   |

> [!NOTE] 
> If `TMPFS` is set to `1`, downloads will be deleted after archiving regardless of `KEEP_DOWNLOADS` value.

#### Exit Codes

| Code 	| Meaning             	|
|------	|---------------------	|
| 0    	| Success             	|
| 16   	| rclone failure      	|
| 32   	| tmpfs mount failure 	|

### Workflow

1. Mounts tmpfs at `/app/downloads` if `TMPFS` equals 1. <br />
2. Run it-claws, retrying up to `MAX_TRIES` times with `RETRY_DELAY` seconds delay.
3. Delete downloads if `TMPFS=1` or `KEEP_DOWNLOADS=0`.
4. Syncs archive to `RC_REMOTE_PATH` using rclone.

### Notes

- The tmpfs will be used to store downloaded files and the result archive.
- Requires preconfigured rclone with valid `RC_REMOTE_PATH`.
- Set `TMPFS_SIZE` based on available memory to avoid mount errors.
- Use `--privileged` Docker option for tmpfs mounting.
- If `TMPFS=1`, downloads are deleted regardless of `KEEP_DOWNLOADS`.