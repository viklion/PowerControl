```
# main.yaml主程序配置文件

log:
    level: INFO    #日志等级
    keep_days: 7    #日志保留天数，0为只保留当天的日志
message:
    enabled: False    #是否启用消息推送
    bemfa_reconnect: True    #是否推送巴法重连消息
    ServerChan_turbo:    #Server酱turbo推送参数配置
      enabled: False    #是否启用
      SendKey: YOUR SENDKEY    #Server酱turbo的key
      channel: 9    #消息通道，默认为9（微信服务号）
    ServerChan3:     #Server酱3推送参数配置
      enabled: False    #是否启用
      SendKey: YOUR SENDKEY    #Server酱3的key
    Qmsg:    #qq消息推送参数配置
      enabled: False    #是否启用
      key: YOUR KEY    #Qmsg酱的key
      qq: 123456789    #QQ号
    WeChat_webhook:    #企业微信机器人消息推送参数配置
      enabled: False    #是否启用
      url: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx
    Gotify:    #Gotify消息推送参数配置
        enabled: False    #是否启用
        url: http(s)://ip:port    #自建服务地址，勿省略http(s)://
        token: YOUR APPS TOKEN    #APPS中的token
    PushPlus:    #PushPlus消息推送参数配置
        enabled: False    #是否启用
        token: YOUR TOKEN    #PushPlus的token
        channel: wechat    #消息通道，默认为wechat（微信服务号）
    Bark:    #Bark消息推送参数配置
        enabled: False    #是否启用
        url: YOUR BARK URL    #服务地址，官方或自建，勿省略http(s)://
        key: YOUR KEY    #服务的Key
    WeChat_app:    #企业微信应用消息推送参数配置
        enabled: False    #是否启用
        corpid: YOUR CORPID    #企业微信-企业ID
        agentid: YOUR AGENTID    #企业微信-应用AgentId
        secret: YOUR SECRET    #企业微信-应用Secret
```
```
# device.yaml设备配置文件

order: 1    #设备排序
main:
  enabled: True    #设备服务总开关
  alias:    #api别名
bemfa:    #巴法参数配置
  enabled: False    #是否连接巴法平台
  uid: aaabbbcccdddeeefffggg    #巴法uid
  topic: mypc001    #巴法设备主题
devices:    #设备参数配置
  name: 电脑    #设备昵称
  ip: 192.168.100.100    #设备局域网ip地址
  wol:    #网络唤醒参数配置
    enabled: True    #是否启用网络唤醒
    method:    #网络唤醒方法
      wakeonlan: True    #内置网络唤醒方法
      shell: False    #自定义指令唤醒
    mac: 00-11-22-33-44-55    #设备网卡mac地址xx-xx格式或xx:xx格式
    destination: broadcast_ip_global    #网络唤醒发送地址，broadcast_ip_global：全局广播（255.255.255.255），broadcast_ip_direct：定向广播（设备所在网段的广播地址），device_ip：设备ip地址
    port: 9    #网络唤醒端口，一般无需修改，默认：9
    interface: default    #指定网卡，default：默认网卡ip，多网卡下可修改成指定ip地址
    shell_script: yourscript    #自定义指令内容
  shutdown:    #关机参数配置
    enabled: True    #是否启用关机
    method:     #关机方法
      netrpc: True    #通过关机账户
      udp: False    #通过配套软件
      shell: False    #通过自定义指令
    account: youraccount    #关机账户-账户
    password: yourpassword    #关机账户-密码
    shell_script: yourscript    #自定义指令内容
    udp_port: 17678    #配套软件监听的端口，默认：17678
    win_cmd: shutdown    #shutdown：关机，reboot：重启，sleep：睡眠，hibernate：休眠
    time: 60    #延迟关机时长，1为立刻关机
    timeout: 2    #指令超时时长，默认：2
  ping:    #ping查询设备在线状态参数配置
    enabled: True    #是否启用ping查询设备在线状态
    time: 60    #查询间隔时长
    method:    #ping方法
      pcping: True    #内置ping方法
      shell: False    #自定义指令ping
    shell_script: yourscript    #自定义指令内容
    on_keyword: 'on'    #判断设备在线关键字
    off_keyword: 'off'    #判断设备离线关键字
message:
    enabled: False     #该设备的消息推送开关
schedule:    #定时任务参数配置
  enabled: False    #是否启用定时任务
  plans:    #定时任务列表
    - id: '1'    #任务id
      enabled: False    #是否启用该任务
      name: '示例任务1'    #任务名称
      type: cron    #任务类型，cron：循环任务，datetime：单次任务
      datetime: '2026-1-1 20:00:00'    #单次任务时间
      cron: '0 9 * * 1-5'    #循环任务时间，5段cron表达式
      action: shutdown    #任务执行操作，wol：开机，shutdown：关机
      remind: False    #是否启用任务执行前提醒
      advance: 5    #任务提前提醒时间，单位：分钟
```

