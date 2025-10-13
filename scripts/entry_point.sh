#!/bin/sh 

echo "[INFO] Creating symbolic links for app configuration files"

mkdir -p /config/app /config/rclone

if [ ! -L /app/config ] && [ -d /app/config ]; then
    rm -rf /app/config
fi
ln -sf /config/app /app/config

echo "[INFO] Executing "$@""

exec "$@"