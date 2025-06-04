# iStoreOS添加容器详细指引
1. docker-镜像，输入`viklion/powercontrol:latest`，点击`拉取`

   ![ist04](https://github.com/user-attachments/assets/e009eefc-0784-46e6-b843-e705983dd201)

1. docker-容器，点击`新增`

   ![ist01](https://github.com/user-attachments/assets/53e79294-d497-4770-94f1-774586779a6b)

1. 容器名称：`powercontrol`

   Docker镜像，选择`viklion/powercontrol:latest`

   勾选`总是先拉取镜像`

   重启策略：选择`Unless stopped`

   网络：选择`host`

   环境变量(别忘了点击'+'号)：`WEB_PORT=你想设置的端口号，默认：7678` , `WEB_KEY=你想设置的密钥，默认：admin`

   绑定挂载(别忘了点击'+'号)：`/dockerdata/powercontrol:/app/data`或者`你自定义的存放配置文件和日志文件的文件夹:/app/data`

   ![ist02](https://github.com/user-attachments/assets/bd06b961-9e4a-44ec-86f8-6dec2a83c6b4)

1. 勾选容器，点击`启动`

   ![ist03](https://github.com/user-attachments/assets/246ca6c2-8bca-42ad-94c8-eb908f932230)

1. 访问`ip:端口`进入首页，顶部跳转教程，输入KEY跳转配置
