![logo](https://github.com/user-attachments/assets/8738de3a-23a3-48d1-bb91-23b152551122)

# PowerControl
docker容器远程网络唤醒设备，远程关闭Windows、Linux、MacOS，可通过访问api控制，并可依赖巴法云接入米家，通过米家远程操作（需要小爱音箱），支持接入homeassistant  
**米家控制受米家、巴法平台稳定性因素影响*  
`linux/amd64, linux/arm/v7, linux/arm64, linux/386`

## 部署
* [视频教程(bilibili)](https://www.bilibili.com/video/BV1cykZY7Er9)

* 小白级详细部署教程：[UNRAID](https://github.com/viklion/PowerControl/blob/main/UNRAID.md) • [群晖](https://github.com/viklion/PowerControl/blob/main/DSM.md) • [飞牛](https://github.com/viklion/PowerControl/blob/main/FNOS.md) • [iStoreOS](https://github.com/viklion/PowerControl/blob/main/iStoreOS.md)

<hr>

不要直接复制命令运行，需要修改参数  
> 1、将容器/app/data目录映射到你的主机目录，存放配置文件和日志文件:  
&nbsp;&nbsp;&nbsp;&nbsp;`修改/your/path`  
2、修改环境变量：  
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_PORT：网页端口`  
&nbsp;&nbsp;&nbsp;&nbsp;`WEB_KEY：密钥`

**不设置环境变量则使用默认参数`port：7678`，`key：admin`*
### 1、Docker CLI
+ 默认root用户运行
```
docker run -d -v /your/path:/app/data -e WEB_PORT=7678 -e WEB_KEY=admin --network host --restart unless-stopped --name powercontrol viklion/powercontrol:latest
```
+ 设置指定user运行（环境变量PUID和PGID）  
**重要：切换非root运行，如遇写入错误，请递归修改映射目录的读写权限（配置文件、日志文件）*
```
docker run -d -v /your/path:/app/data -e WEB_PORT=7678 -e WEB_KEY=admin -e PUID=1000 -e PGID=100 --network host --restart unless-stopped --name powercontrol viklion/powercontrol:latest
```

### 2、Docker Compose
```
services:
  powercontrol:
    image: viklion/powercontrol:latest
    container_name: powercontrol
    volumes:
      - /your/path:/app/data
    environment:
      - WEB_PORT=7678
      - WEB_KEY=admin
      # 默认root用户运行，去掉下两行的#，设置指定user运行
      #- PUID=1000
      #- PGID=100
    restart: unless-stopped
    network_mode: host
```

## 配置
访问`ip:端口`进入首页，顶部跳转教程，输入KEY跳转配置

一般无需手动修改config.yaml配置文件，都可在web配置，[配置文件参数详解](https://github.com/viklion/PowerControl/blob/main/YAML.md)

## 界面
![index](https://github.com/user-attachments/assets/3df4b928-0cf9-4deb-a478-5681dc77b586)

![config](https://github.com/user-attachments/assets/ac7eba15-5e32-4495-a015-931a4e3ca7a6)


