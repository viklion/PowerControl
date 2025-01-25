# 使用官方的 Python 作为基础镜像
FROM python:3.12.8-alpine

# 维护者、贡献者、版本
LABEL maintainer="viklion" \
      contributors="Aliang-code" \
      version="2.5" 

# 设置时区
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器中的 /app 目录
COPY . /app

# 安装包
RUN apk add --no-cache --update libcap tzdata samba sshpass curl && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    rm -rf /var/cache/apk/* && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod u+s /bin/ping && \
    setcap cap_net_raw+ep $(which python3.12)

# 设置容器启动时运行的命令
CMD ["python", "PCrun.py"]

