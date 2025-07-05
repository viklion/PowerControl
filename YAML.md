```
# config.yaml

bemfa:    #巴法参数配置
  enabled: False    #是否连接巴法平台
  uid: aaabbbcccdddeeefffggg    #巴法uid
  topic: mypc001    #巴法设备主题
devices:    #设备参数配置
  name: 电脑    #设备昵称
  ip: 192.168.100.100    #设备局域网ip地址
  wol:    #网络唤醒参数配置
    enabled: True    #是否启用网络唤醒
    mac: 00-11-22-33-44-55    #设备网卡mac地址xx-xx格式或xx:xx格式
    destination: broadcast_ip_global    #网络唤醒发送地址，broadcast_ip_global：全局广播（255.255.255.255），broadcast_ip_direct：定向广播（设备所在网段的广播地址），device_ip：设备ip地址
    port: 9    #网络唤醒端口，一般无需修改，默认：9
    interface: default    #指定网卡，default：默认网卡ip，多网卡下可修改成指定ip地址
  shutdown:    #关机参数配置
    enabled: True    #是否启用关机
    method:     #关机方法
      netrpc: True    #通过关机账户
      udp: False    #通过配套软件
      shell: False    #通过自定义指令
    account: youraccount    #关机账户-账户
    password: yourpassword    #关机账户-密码
    shell_script: yourscript    #自定义指令
    shell_script_allowed:    #允许的指令参数配置
      - sshpass    #非交互式ssh指令
      - curl    #发送网络请求指令
    time: 60    #延迟关机时长，1为立刻关机
    timeout: 2    #指令超时时长，默认：2
  ping:    #ping查询设备在线状态参数配置
    enabled: True    #是否启用ping查询设备在线状态
    time: 60    #查询间隔时长
functions:    #其他功能参数配置
  log:    #日志功能参数配置
    enabled: True    #是否启用日志记录
    level: 2    #日志等级，1:记录服务器返回数据和ping结果、操作、报错 2:记录操作和报错 3:记录报错
    clear_log:     #自动清理日志参数配置
      enabled: False    #是否启用自动清理日志
      keep_days: 7    #日志保留天数，0为只保留当天的日志
  push_notifications:    #消息推送参数配置
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
      url: 示例 https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx
```