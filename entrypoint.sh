#!/bin/sh
Green="\033[32m"
Red="\033[31m"
Yellow='\033[33m'
Font="\033[0m"
INFO="[${Green}INFO${Font}]"
ERROR="[${Red}ERROR${Font}]"
WARN="[${Yellow}WARN${Font}]"
function INFO() {
    echo -e "${INFO} ${1}"
}
function ERROR() {
    echo -e "${ERROR} ${1}"
}
function WARN() {
    echo -e "${WARN} ${1}"
}

: "${PUID:=0}"
: "${PGID:=0}"
: "${TZ:=Asia/Shanghai}"

ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime
echo ${TZ} > /etc/timezone
groupmod -o -g "${PGID}" powercontrol
usermod -o -u "${PUID}" powercontrol

if [ -n "$APK_ADD" ]; then
    INFO "准备安装：$APK_ADD"

    output=$(apk add --no-cache $APK_ADD 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        INFO "$output\n"
        INFO "安装完毕"
    else
        ERROR "$output\n"
        ERROR "安装失败"
    fi

    rm -rf /var/cache/apk/*
fi

if [ -n "$SHELL_ADD" ]; then
    INFO "准备执行：$SHELL_ADD"
    output=$(eval "$SHELL_ADD" 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        INFO "$output\n"
        INFO "执行完毕"
    else
        ERROR "$output\n"
        ERROR "执行失败"
    fi
fi

chown -R powercontrol:powercontrol /app
INFO "PowerControl启动：VERSION=$VERSION UID=$PUID GID=$PGID"

exec su-exec powercontrol "$@"