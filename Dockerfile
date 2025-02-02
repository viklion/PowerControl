# 使用官方的 Python 作为基础镜像
FROM python:3.12.8-alpine

# 信息
LABEL name="PowerControl" \
      maintainer="viklion" \
      github="https://github.com/viklion/PowerControl"

# 设置参数
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 安装包、其他操作
RUN apk add --no-cache --update shadow libcap tzdata samba sshpass curl openssh-client && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    rm -rf /var/cache/apk/* && \
    chmod u+s /bin/ping && \
    setcap cap_net_raw+ep $(which python3.12)

# 复制一般不会有变动的文件
COPY software /app/static
COPY requirements.txt /app

# 安装python模块
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt

# 创建一些用户和组
RUN for i in $(seq 1000 1005); do \
        useradd -d /app -u $i -g 100 PCuser$i; \
        groupadd -g $i PCuser$i; \
    done

# 复制其他文件
COPY doc /app/static
COPY app /app

# 设置容器启动时运行的命令
CMD ["python", "PCrun.py"]

