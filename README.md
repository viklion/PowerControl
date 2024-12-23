![logo](https://pic.viklion.com/s/2024/12/20/676553945ec8d.png)
# PowerControl
docker容器远程网络唤醒设备，远程关闭windows设备，并可依赖巴法云接入米家，通过米家远程操作<br>
linux/amd64,linux/arm/v7,linux/arm64,linux/386

## 安装
不要直接复制命令运行，需要修改参数<br>
1、将容器/app/data目录映射到你的主机目录，存放配置文件和日志文件:<br>
&nbsp;&nbsp;&nbsp;&nbsp;`修改/your/path`<br>
2、修改环境变量：<br>
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_PORT：网页端口`<br>
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_KEY：密钥`

### 1、Docker
```
docker run -d --restart unless-stopped -v /your/path:/app/data -e WEB_PORT=7678 -e WEB_KEY=yourkey --network host --name powercontrol viklion/powercontrol:latest
```

### 2、Docker-Compose
```
services:
    powercontrol:
        image: viklion/powercontrol:latest
        container_name: powercontrol
        restart: unless-stopped
        network_mode: host
        volumes:
            - /your/path:/app/data
        environment:
            - WEB_PORT=7678
            - WEB_KEY=yourkey
```

## 配置
查看仓库内pdf教程（最新）<br>
访问 ip:端口 查看教程（不一定是最新）
