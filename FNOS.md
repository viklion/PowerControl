# 飞牛添加容器详细指引（[常规](https://github.com/viklion/PowerControl/blob/main/FNOS.md#常规部署) 或 [compose](https://github.com/viklion/PowerControl/blob/main/FNOS.md#compose部署)）
## 常规部署
> * *如需非root用户启动容器，可选择命令行部署或compose部署*
1. 打开docker

   点击`镜像仓库`

   右上角输入`powercontrol`回车

   找到`viklion/powercontrol`点击下载图标

   选择标签`latest`

   ![20250603183549_1](https://github.com/user-attachments/assets/8a6307a8-2f08-4261-84d6-26fde55e7561)

1. 点击容器-添加容器

   镜像名称选择`viklion/powercontrol:latest`

   容器名称：`powercontrol`（可自由更改）

   点击`开机自动开启`（其实就是“启用自动重新启动”，即容器异常退出会自动重启容器，不知道为什么飞牛要写成“开机自动开启”）

   ![20250603183550_2](https://github.com/user-attachments/assets/5ca6d4f3-1d25-4d2a-a283-9dae46055889)

1. 存储位置-点击添加路径，选择存放配置文件和日志文件的文件夹

   ![20250603183550_3](https://github.com/user-attachments/assets/677c15ee-01be-4e78-95ea-0f978478d0c9)

   ![20250603183549_4](https://github.com/user-attachments/assets/eee75ca5-1d70-41f0-b32e-b0471ded989f)

1. 填入映射的容器文件夹`/app/data`

   ![20250603183550_5](https://github.com/user-attachments/assets/c8c8f0e2-6ce4-4e7a-8114-da2af74abae1)

1. 环境变量新增：

   `WEB_PORT`  `填入你想设置的端口号，默认：7678`

   `WEB_KEY`  `填入你想设置的密钥，默认：admin`

   ![20250603183550_6](https://github.com/user-attachments/assets/3eac7a64-9f0a-49dd-a4de-f3edeed7d34a)

1. 网络选择`host`

   ![20250603183549_7](https://github.com/user-attachments/assets/23c93184-85f6-449f-8b10-10b7b1ae1f2d)

## compose部署
1. 打开docker

   点击`Compose`

   点击`新增项目`

1. 项目名称：`powercontrol`（可自由更改）

   路径：选择存放compose配置文件的文件夹

   来源：选择`创建docker-compose.yml`

   点击本项目github首页中Docker Compose右上角复制按钮，粘贴到下方

   修改相关参数（如何查看映射文件夹完整路径、如何查看uid和gid见下方）

   ![fn01](https://github.com/user-attachments/assets/f0020dbc-35e3-4f0c-b0f1-4ec3716a2931)

1. 查看映射文件夹完整路径

   打开`文件管理`

   定位到需要存放容器配置和日志的文件夹

   右键文件夹，点击`详细信息`

   点击`位置`中的`复制原始路径`

   替换compose yml中的`/your/path`

   ![fn02](https://github.com/user-attachments/assets/68daa13b-41cf-4b69-97a0-5faa888a18ea)

   ![fn03](https://github.com/user-attachments/assets/5da4e3b3-eaa0-4240-87c9-fd884a985a32)

1. （选填）如需非root用户启动容器，查询uid和gid

   ssh连上飞牛

   输入id 登录用户名，如`id viklion`

   ![fn04](https://github.com/user-attachments/assets/2bbaf4d2-971d-4809-9bc3-bc5d51c2e594)
