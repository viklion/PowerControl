# 群晖添加容器详细指引（[常规](https://github.com/viklion/PowerControl/blob/main/DSM.md#常规部署) 或 [compose](https://github.com/viklion/PowerControl/blob/main/DSM.md#compose部署)）
## 常规部署

1. 打开Container Manager

   点击注册表

   右上角输入`powercontrol`

   点击`viklion/powercontrol`

   点击下载

   选择标签`latest`

   ![dsm01](https://github.com/user-attachments/assets/92a9d65f-2c76-4fa6-9811-c751d21edc61)

1. 点击容器-新增

   映像选择`viklion/powercontrol:latest`

   容器名称：`powercontrol`（可自由更改）

   点击`启用自动重新启动`

   ![dsm02](https://github.com/user-attachments/assets/5cf8ff9a-2896-4d4f-b903-e1159135e047)

1. 点击添加文件夹，选择存放配置文件和日志文件的文件夹

   ![dsm03](https://github.com/user-attachments/assets/0cbd9a25-5151-4ffa-a8eb-4163bf6858a1)

1. 填入映射的容器文件夹`/app/data`

   ![dsm04](https://github.com/user-attachments/assets/017ac052-46e2-44a7-9600-4a37687ffab3)

1. 环境变量新增：

   `WEB_PORT`  `填入你想设置的端口号，默认：7678`

   `WEB_KEY`  `填入你想设置的密钥，默认：admin`

   >（以下选填）非root用户启动，[查询uid和gid](https://github.com/viklion/PowerControl/blob/main/DSM.md#查询uid和gid)：  
   > `PUID`  `填入uid`  
   > `PGID`  `填入gid`

   ![dsm05](https://github.com/user-attachments/assets/bba761ff-bc54-4952-92ae-1ff0d183c75f)

1. 网络选择`host`

   ![dsm06](https://github.com/user-attachments/assets/9413fe65-fdc6-4113-bf33-53cc090f87bc)

1. 容器启动后访问`ip:端口`进入首页，顶部跳转教程，输入KEY跳转配置

## compose部署
1. 打开Container Manager

   点击`项目`

   点击`新增`

   ![dsm08](https://github.com/user-attachments/assets/84b7cd1c-eeed-4887-a3e3-a2a72a8371a5)

1. 项目名称：`powercontrol`（可自由更改）

   路径：选择存放compose配置文件的文件夹

   来源：选择`创建docker-compose.yml`

   点击本项目github首页中Docker Compose右上角复制按钮，粘贴到下方

   修改相关参数（如何查看映射文件夹完整路径、如何查看uid和gid见下方）

   容器启动后访问`ip:端口`进入首页，顶部跳转教程，输入KEY跳转配置

   ![dsm001](https://github.com/user-attachments/assets/b843a5b2-b54a-4797-8aab-8bbba324f447)

1. 查看映射文件夹完整路径

   打开`File Station`

   定位到需要存放容器配置和日志的文件夹

   右键文件夹，点击`属性`

   复制`位置`中的路径

   替换compose yml中的`/your/path`

   ![dsm10](https://github.com/user-attachments/assets/fccc4f82-1da1-4203-9c54-3d9c7ac978d6)

   ![dsm11](https://github.com/user-attachments/assets/58bb28b1-dcdc-43ff-a487-10fc4e617b3e)

## 查询uid和gid

   ssh连上群晖

   输入id 登录用户名，如`id viklion`

   ![dsm12](https://github.com/user-attachments/assets/5501786c-2b9f-4d4e-8a77-3cbbcded8213)

