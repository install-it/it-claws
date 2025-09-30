#!/bin/bash

DATA_PATH="/app/downloads"
DOWNLOAD_DIR="$DATA_PATH/${DOWNLOAD_DIR_NAME:-downloads}"
ARCHIVE_PATH="$DATA_PATH/${ARCHIVE_NAME:-driver-pack.zip}"
MAX_RETRIES=${MAX_RETRIES:-3}
RETRY_DELAY=${MAX_RETRIES:-10}

mkdir -p $DATA_PATH
if [ "${CREATE_RAM_DISK:-1}" = "1" ]; then
    mount -t tmpfs -o size=${RAM_DISK_SIZE:-24G} tmpfs $DATA_PATH
fi

for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "Attempt $i of $MAX_RETRIES"
    python /app/src/main.py -d "${DOWNLOAD_DIR}" -o "$OUTPUT_ZIP" $((( i > 1 )) && echo "-r") "${ARGUMENTS}"

    if [ $? -eq 0 ]; then
        echo "it-claws executed successfully"
        echo "Uploading output using rclone..."
        rclone sync "$ARCHIVE_PATH" "${RC_REMOTE_PATH}"
        exit 0
    else
        echo "it-claws executes failed"
        if [ $i -lt $MAX_RETRIES ]; then
            echo "Retrying in $RETRY_DELAY seconds..."
            sleep $RETRY_DELAY
        fi
    fi
done

echo "it-claws failed after $MAX_RETRIES attempts"
exit 1