# 使用官方的 Python 作为基础镜像
FROM python:3.12.8-alpine

# 信息
LABEL name="PowerControl" \
      maintainer="viklion" \
      github="https://github.com/viklion/PowerControl"

# 设置工作目录
WORKDIR /app

# 安装包、其他操作
RUN apk add --no-cache --update shadow libcap tzdata samba sshpass curl openssh-client su-exec && \
    rm -rf /var/cache/apk/* && \
    chmod u+s /bin/ping && \
    setcap cap_net_raw+ep $(which python3.12) && \
    groupadd -r powercontrol -g 666 && \
    useradd -r powercontrol -g powercontrol -d /app

# 安装python模块
COPY --chmod=755 requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制文件
COPY --chmod=755 software /app/static/
COPY --chmod=755 doc /app/static/
COPY --chmod=755 app LICENSE entrypoint.sh /app/
RUN chmod +x entrypoint.sh

# 版本
ENV VERSION=3.1

# 容器启动时运行的命令
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "PCrun.py"]