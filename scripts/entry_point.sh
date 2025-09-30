#!/bin/sh 

echo "**** creating symbolic links for configuration files ****"

mkdir -p /config/app /config/rclone

ln -sf /config/app /app/config
ln -sf /config/rclone/ $(dirname $(rclone config file | sed -n 2p))

exec "$@"