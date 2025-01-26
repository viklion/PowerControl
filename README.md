![logo](https://pic.viklion.com/s/2024/12/20/676553945ec8d.png)
# PowerControl
docker容器远程网络唤醒设备，远程关闭windows设备，通过访问网页控制，并可依赖巴法云接入米家，通过米家远程操作（需要小爱音箱）<br>
**米家控制受米家、巴法平台稳定性因素影响*<br>
linux/amd64,linux/arm/v7,linux/arm64,linux/386

## 部署
[视频教程(bilibili)](https://www.bilibili.com/video/BV1cykZY7Er9)

不要直接复制命令运行，需要修改参数<br>
1、将容器/app/data目录映射到你的主机目录，存放配置文件和日志文件:<br>
&nbsp;&nbsp;&nbsp;&nbsp;`修改/your/path`<br>
2、修改环境变量：<br>
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_PORT：网页端口`<br>
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_KEY：密钥`

**不设置环境变量则使用默认参数port：7678，key：admin*
### 1、Docker
+ 默认root用户运行
```
docker run -d -v /your/path:/app/data -e WEB_PORT=7678 -e WEB_KEY=yourkey --network host --restart unless-stopped --name powercontrol viklion/powercontrol:latest
```
+ 设置指定user运行（-u uid:gid）<br>
**重要：如果切换非root运行，请务必检查映射目录的读写权限（配置文件、日志文件），如遇写入错误，请递归修改权限*
```
docker run -d -u 1000:100 -v /your/path:/app/data -e WEB_PORT=7678 -e WEB_KEY=yourkey --network host --restart unless-stopped --name powercontrol viklion/powercontrol:latest
```

### 2、Docker-Compose
```
services:
  powercontrol:
    image: viklion/powercontrol:latest
    container_name: powercontrol
    volumes:
      - /your/path:/app/data
    environment:
      - WEB_PORT=7678
      - WEB_KEY=yourkey
    # 默认root用户运行，去掉下行的#，设置指定user运行（uid:gid）
    #user: 1000:100
    restart: unless-stopped
    network_mode: host
```

## 配置
访问 ip:端口 查看教程
