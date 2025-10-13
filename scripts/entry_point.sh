#!/bin/sh 

echo "[INFO] Creating symbolic links for configuration files"

mkdir -p /config/app /config/rclone

if [ ! -L /app/config ] && [ -d /app/config ]; then
    rm -rf /app/config
fi
ln -sf /config/app /app/config

RCLONE_CONFIG_DIR=$(dirname $(rclone config file | sed -n 2p))
if [ ! -L "$RCLONE_CONFIG_DIR" ] && [ -d "$RCLONE_CONFIG_DIR" ]; then
    rm -rf "$RCLONE_CONFIG_DIR"
fi
ln -sf /config/rclone "$RCLONE_CONFIG_DIR"

echo "[INFO] Executing "$@""

exec "$@"