# UNRAID添加容器详细指引
1. docker界面左下角点击添加容器
   
   ![unraid-01](https://github.com/user-attachments/assets/93eb7afc-b56e-4a1f-8f89-37fbeadbeb82)

1. 名称填入`powercontrol`（可自由更改）

   存储库填入`viklion/powercontrol:latest`

   网络类型选择`Host`

   然后点击添加另一个路径、端口、变量、标签或设备
    
   ![unraid-04](https://github.com/user-attachments/assets/ead45847-37d1-4c82-9a64-ae9243bbf506)

1. 配置类型选择`路径`

   名称：`config`

   容器路径：`/app/data`

   主机路径：`/mnt/user/appdata/powercontrol`

   访问模式：`读/写`

   ![unraid-05](https://github.com/user-attachments/assets/05f3bded-564c-4ae3-a42b-aa0978489611)

1. 再次点击添加另一个路径、端口、变量、标签或设备

   配置类型选择`变量`

   名称：`WEB_PORT`

   键：`WEB_PORT`

   值：`填入你想设置的端口号，默认：7678`

   ![unraid-06](https://github.com/user-attachments/assets/72126401-ce88-43a1-8405-83c43c0ed895)

1. 再次点击添加另一个路径、端口、变量、标签或设备

   配置类型选择`变量`

   名称：`WEB_KEY`

   键：`WEB_KEY`

   值：`填入你想设置的密钥，默认：admin`

   ![unraid-07](https://github.com/user-attachments/assets/0b68c338-1515-4590-bacf-039a0f32b839)

1. 右上角点击高级视图
   
   ![unraid-02](https://github.com/user-attachments/assets/da9104a4-ec17-4d16-8c2f-92db44bbff3b)

1. 额外参数中填入`--restart unless-stopped`
   
   ![unraid-08](https://github.com/user-attachments/assets/7a485371-2694-4bbb-96e4-bed5132cb77f)

1. （选填）非root用户启动容器

   额外参数中填入`-u uid:gid`

   如何查询uid和gid

   右上角点击终端

   ![unraid-03](https://github.com/user-attachments/assets/089039c4-0291-4412-ba56-e175b56525d5)

   输入id 共享访问的用户，如`id viklion`

   ![unraid-09](https://github.com/user-attachments/assets/80ebfd45-edd5-404f-ad70-7d60797595f5)

1. 容器启动后访问`ip:端口`进入首页，顶部跳转教程，输入KEY跳转配置

1. 如果拉取镜像遇到网络（梯子）问题

   尝试将存储库修改为`docker.1panel.live/viklion/powercontrol:latest`
