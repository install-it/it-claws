#!/bin/bash

DATA_PATH="/app/downloads"
DOWNLOAD_DIR="$DATA_PATH/${DOWNLOAD_DIR_NAME:-downloads}"
ARCHIVE_PATH="$DATA_PATH/${ARCHIVE_NAME:-driver-pack.zip}"

TMPFS=${TMPFS:-1}
TMPFS_SIZE=${TMPFS_SIZE:-24G}

mkdir -p "$DATA_PATH"
if [ "$TMPFS" = "1" ]; then
    echo "[INFO] Mounting tmpfs of size $TMPFS_SIZE on $DATA_PATH"
    if ! mount -t tmpfs -o size="$TMPFS_SIZE" tmpfs "$DATA_PATH"; then
        echo "[ERROR] Failed to mount tmpfs"
        exit 32
    fi
fi

python /app/src/main.py \
    -o "$DOWNLOAD_DIR" \
    -a "$ARCHIVE_PATH" \
    --retries "${RETRIES:-1}" \
    --compress-level "${COMPRESS_LEVEL:-5}" \
    $ARGUMENTS

pipeline_exit=$?

if [ $pipeline_exit -eq 0 ]; then
    echo "[INFO] Uploading archive using rclone..."
    if rclone sync -v "$ARCHIVE_PATH" "$RC_REMOTE_PATH"; then
        echo "[INFO] Upload successful"
    else
        echo "[ERROR] rclone sync failed"
        pipeline_exit=16
    fi
fi

if [ "$TMPFS" = "1" ]; then
    echo "[INFO] Unmounting tmpfs..."
    umount "$DATA_PATH" || true
fi

exit $pipeline_exit
