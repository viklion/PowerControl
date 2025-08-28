![logo](https://github.com/user-attachments/assets/8738de3a-23a3-48d1-bb91-23b152551122)

# PowerControl
## 简介
docker容器远程网络唤醒或关闭Windows、Linux、MacOS设备，支持添加多设备，可通过访问api控制，并可依赖巴法云接入米家，通过米家远程操作（需要小爱音箱），支持接入homeassistant  
**米家控制受米家、巴法平台稳定性因素影响*  
`linux/amd64, linux/arm/v7, linux/arm64, linux/386`

## 功能
1. 多种方式唤醒或关闭Windows、Linux、MacOS设备
1. 通过巴法云接入米家，使用小爱音箱语音开机/关机
1. 通过访问api开机/关机，端口转发或反向代理后可远程操作
1. 支持接入homeassistant，通过homeassistant操作
1. 通过自定义指令，可打开/关闭虚拟机
1. 支持多设备管理
1. 支持消息推送

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
**网络模式支持host、ipvlan、macvlan，不支持bridge*
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
访问`ip:端口`进入首页，输入KEY跳转设备总览页，点击卡片进入配置页

一般无需手动修改配置文件，都可在web配置，[配置文件参数详解](https://github.com/viklion/PowerControl/blob/main/YAML.md)

## 界面
![index](https://github.com/user-attachments/assets/3df4b928-0cf9-4deb-a478-5681dc77b586)

![overview](https://github.com/user-attachments/assets/c9cf79ba-c624-46fe-b47a-00bec12bd265)

![config](https://github.com/user-attachments/assets/d272cbd9-0133-4785-a5c0-fba1bcd423f4)

