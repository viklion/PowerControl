#!/bin/sh
: "${PUID:=0}"
: "${PGID:=0}"
: "${TZ:=Asia/Shanghai}"

ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime
echo ${TZ} > /etc/timezone
groupmod -o -g "${PGID}" powercontrol
usermod -o -u "${PUID}" powercontrol
chown -R powercontrol:powercontrol /app
echo "PowerControl启动：VERSION=$VERSION UID=$PUID GID=$PGID"

exec su-exec powercontrol "$@"