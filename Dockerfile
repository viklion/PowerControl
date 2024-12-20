# 使用官方的 Python 运行时作为基础镜像
FROM python:3.12.8-slim

LABEL maintainer="viklion" \
    version="1.3" 

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器中的 /app 目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置容器启动时运行的命令
CMD ["python", "run.py"]

