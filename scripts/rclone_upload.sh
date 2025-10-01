#!/bin/bash

DATA_PATH="/app/downloads"
DOWNLOAD_DIR="$DATA_PATH/${DOWNLOAD_DIR_NAME:-downloads}"
ARCHIVE_PATH="$DATA_PATH/${ARCHIVE_NAME:-driver-pack.zip}"
MAX_RETRIES=${MAX_RETRIES:-3}
RETRY_DELAY=${RETRY_DELAY:-10}

mkdir -p $DATA_PATH
if [ "${TMPFS:-1}" = "1" ]; then
    echo "[INFO] Mounting a tmpfs of size $TMPFS_SIZE on "$DATA_PATH""
    if ! mount -t tmpfs -o size=${TMPFS_SIZE:-24G} tmpfs $DATA_PATH; then
        echo "[ERROR] Failed to mount tmpfs"
        exit 32
    fi
fi

for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "Attempt $i of $MAX_RETRIES"
    
    python /app/src/main.py \
        -d "$DOWNLOAD_DIR" \
        -o "$OUTPUT_ZIP" $((( i > 1 )) && echo "-r") $ARGUMENTS

    if [ $? -eq 0 ]; then
        echo "[INFO] it-claws executed successfully"

        echo "[INFO ]Uploading output using rclone..."
        if rclone sync "$ARCHIVE_PATH" "${RC_REMOTE_PATH}"; then
            echo "[INFO] Upload successful"
            exit 0
        else
            echo "[ERROR] rclone sync failed"
            exit 16
        fi
    else
        if [ $? -eq 4 ] && [ $i -lt $MAX_RETRIES ]; then
            echo "Download job failed, retrying in $RETRY_DELAY seconds..."
            sleep "$RETRY_DELAY"
        else
            echo "it-claws executes failed"
            exit 1
        fi
    fi
done

echo "it-claws failed after $MAX_RETRIES attempts"
exit 1
