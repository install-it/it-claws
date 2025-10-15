#!/bin/bash

DATA_PATH="/app/downloads"
DOWNLOAD_DIR="$DATA_PATH/${DOWNLOAD_DIR_NAME:-downloads}"
ARCHIVE_PATH="$DATA_PATH/${ARCHIVE_NAME:-driver-pack.zip}"

TMPFS=${TMPFS:-1}
TMPFS_SIZE=${TMPFS_SIZE:-24G}
KEEP_DOWNLOADS=${KEEP_DOWNLOADS:-1}

MAX_TRIES=${MAX_TRIES:-3}
RETRY_DELAY=${RETRY_DELAY:-10}

mkdir -p $DATA_PATH
if [ $TMPFS = "1" ]; then
    echo "[INFO] Mounting a tmpfs of size $TMPFS_SIZE on "$DATA_PATH""
    echo "[DEBUG] Memory available: `free --human | grep Mem | awk '{print $4}'`"
    if ! mount -t tmpfs -o size=$TMPFS_SIZE tmpfs $DATA_PATH; then
        echo "[ERROR] Failed to mount tmpfs"
        exit 32
    fi
fi

for ((i=1; i<=MAX_TRIES; i++)); do
    echo "[INFO] Attempt $i of $MAX_TRIES"
    
    python /app/src/main.py \
        -d "$DOWNLOAD_DIR" \
        -o "$ARCHIVE_PATH" $((( i > 1 )) && echo "-r") $ARGUMENTS

    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[INFO] it-claws executed successfully"
        break
    elif [ $exit_code -eq 4 ] && [ $i -lt $MAX_TRIES ]; then
            echo "[WARN] Some download failed, retrying in $RETRY_DELAY seconds..."
            sleep "$RETRY_DELAY"
    else
        echo "[ERROR] it-claws executes failed"
        exit 1
    fi
done

if [ $TMPFS = "1" ] || [ $KEEP_DOWNLOADS = "0" ]; then
    echo "[INFO] Removing download files..."
    find "$DOWNLOAD_DIR" -maxdepth 1 ! -path "$ARCHIVE_PATH" -exec rm -rf {} +
fi

echo "[INFO] Uploading output using rclone..."
if rclone sync -v "$ARCHIVE_PATH" "$RC_REMOTE_PATH"; then
    echo "[INFO] Upload successful"
    exit 0
else
    echo "[ERROR] rclone sync failed"
    exit 16
fi
