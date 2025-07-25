import socket, time
from PCfunctions import write_log, send_message, pcwol, pcshutdown, get_time, extra_log
from datetime import datetime

class PCbemfa():
    def __init__(self ,funcs_data):
        self.server_ip = 'bemfa.com'
        self.server_port = 8344
        self.fd = funcs_data
        self.enabled = self.fd.bemfa_enabled
        if self.enabled:
            self.uid = self.fd.bemfa_uid
            self.topic = self.fd.bemfa_topic
            self.ping_enabled = self.fd.ping_enabled
            self.bemfa_reconnect_count = 0
            extra_log("bemfa初始化成功",2, '_bemfa')

    # 订阅
    def connTCP(self):
        while True:
            try:
                # 创建socket
                self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_client_socket.settimeout(120)
                # 连接服务器
                self.tcp_client_socket.connect((self.server_ip, self.server_port))
                # 发送订阅指令
                substr = f'cmd=1&uid={self.uid}&topic={self.topic}\r\n'
                self.tcp_client_socket.send(substr.encode('utf-8'))
                # 写入日志
                extra_log("bemfa订阅成功", 2, '_bemfa')
                break
            except:
                extra_log("bemfa订阅失败，1分钟后重试...", 3, '_bemfa')
            time.sleep(60)

    # 心跳
    def send_heartbeat_packet(self):
        # 发送心跳
        try:
            self.tcp_client_socket.send('ping\r\n'.encode('utf-8'))
            write_log("已发送bemfa心跳包",1,'_bemfa')
        except:
            extra_log("发送bemfa心跳包失败",3, '_bemfa')
    
    # 开启定时发送心跳包
    def add_send_heartbeat_packet_job(self):
        try:
            self.fd.scheduler.add_job(self.send_heartbeat_packet, 'interval', seconds=60, next_run_time=datetime.now(), id='send_heartbeat_packet_job')
            extra_log("bemfa心跳包定时发送已启动", 2, '_bemfa')
        except Exception as e:
            extra_log("开启bemfa心跳包定时发送任务失败："+str(e),3, '_bemfa')

    # 关闭定时发送心跳包
    def remove_send_heartbeat_packet_job(self):
        try:
            self.fd.scheduler.remove_job('send_heartbeat_packet_job')
            extra_log("关闭bemfa心跳包定时发送", 2, '_bemfa')
        except Exception as e:
            extra_log("关闭bemfa心跳包定时发送任务失败："+str(e),3, '_bemfa')

    # 更新巴法云的设备状态
    def update_bemfa(self):
        pc_state = self.fd.pc_state
        if "on" in pc_state or "off" in pc_state:
            try:
                substr = f'cmd=2&uid={self.uid}&topic={self.topic}/up&msg={pc_state[1]}\r\n'
                self.tcp_client_socket.send(substr.encode("utf-8"))
                write_log("bemfa设备状态更新："+pc_state[0], 1, '_bemfa')
            except Exception as e:
                extra_log("更新bemfa设备状态失败："+str(e),3, '_bemfa')
    
    # 开启定时更新巴法云的设备状态
    def add_update_bemfa_job(self):
        if self.ping_enabled:
            try:
                self.fd.scheduler.add_job(self.update_bemfa, 'interval', seconds=60, next_run_time=datetime.now(), id='update_bemfa_job')
                extra_log("bemfa设备状态定时更新已启动", 2, '_bemfa')
            except Exception as e:
                extra_log("开启bemfa设备状态定时更新任务失败："+str(e),3, '_bemfa')

    # 关闭定时更新巴法云的设备状态
    def remove_update_bemfa_job(self):
        if self.ping_enabled:
            try:
                self.fd.scheduler.remove_job('update_bemfa_job')
                extra_log("关闭bemfa设备状态定时更新", 2, '_bemfa')
            except Exception as e:
                extra_log("关闭bemfa设备状态定时更新任务失败："+str(e),3, '_bemfa')

    # 重置重连次数
    def reset_reconnect_count(self):
        self.bemfa_reconnect_count = 0

    # 重置重连次数定时任务
    def add_reset_reconnect_count_job(self):
        self.fd.scheduler.add_job(self.reset_reconnect_count, 'cron', hour=0, minute=0, id='reset_reconnect_count_job')

    # 收到消息后执行开关机
    def power_control(self, state):
        if state == 'on' :
            rs = pcwol()
            if rs:
                if 'done' in rs:
                    extra_log('已发送唤醒指令(bemfa)',2, '_bemfa')
                    send_message('已发送唤醒指令')
                else:
                    extra_log('发送唤醒指令失败(bemfa)' + ' → ' + rs ,3, '_bemfa')
                    send_message('发送唤醒指令失败')
            else:
                extra_log('未启用网络唤醒(bemfa)' ,3, '_bemfa')
                send_message('未启用网络唤醒')
        elif state == 'off':
            rs = pcshutdown()
            if rs:
                if 'succeeded' in rs:
                    extra_log("已发送关机指令(bemfa)" + ' → ' + rs ,2, '_bemfa')
                    send_message('已发送关机指令')
                else:
                    extra_log("关机指令发送失败(bemfa)" + ' → ' + rs ,3, '_bemfa')
                    send_message('关机指令发送失败')
            else:
                extra_log('未启用远程关机(bemfa)' ,3, '_bemfa')
                send_message('未启用远程关机')

    # 主循环
    def mainloop(self):
        while True:
            try:
                # 接收服务器发送过来的数据
                recv_Data = self.tcp_client_socket.recv(1024)
                recv_str = str(recv_Data.decode('utf-8'))
                write_log(recv_str.replace('\n', '').replace('\r', ''),1,'_bemfa')
            except Exception as e:
                extra_log("接收bemfa服务器消息出错，重新订阅...Error: " + str(e), 3, '_bemfa')
                break

            if not recv_Data:
                extra_log("bemfa服务器未返回任何数据，重新订阅...",3, '_bemfa')
                break

            elif f'uid={self.uid}' in recv_str:
                # 收到开机消息
                if 'msg=on' in recv_str:
                    self.power_control('on')
                # 收到关机消息
                elif 'msg=off' in recv_str:
                    self.power_control('off')

    # 启动
    def run(self, retry=False):
        if self.enabled:
            if not retry:
                extra_log("bemfa服务启动",2, '_bemfa')
                self.add_reset_reconnect_count_job()
            elif retry:
                self.bemfa_reconnect_count += 1
                extra_log(f"正在重新订阅bemfa(今日第{self.bemfa_reconnect_count}次)",2, '_bemfa')
                self.remove_send_heartbeat_packet_job()
                self.remove_update_bemfa_job()
                if self.fd.push_enabled:
                    if self.fd.push_bemfa_reconnect:
                        if self.bemfa_reconnect_count <= 5: 
                            send_message( f'重新订阅bemfa提醒', desp=f'正在重新订阅bemfa(今日第{self.bemfa_reconnect_count}次)\n\n断连时间：{get_time()}\n\n可能的原因：网络发生短暂断开；bemfa服务器偶然断连。\n\n*当天重连推送达5次后将不再推送，请查看日志。', retry=True)
                        elif self.bemfa_reconnect_count == 6:
                            extra_log("今日重连推送已达5次，将不再推送", 2, '_bemfa')
                try:
                    self.tcp_client_socket.close()
                except Exception as e:
                    extra_log("关闭TCP连接失败，Error: " + str(e), 3, '_bemfa')
                if self.bemfa_reconnect_count > 5:
                    if self.bemfa_reconnect_count == 6:
                        extra_log(rf"今日重连已达5次，后续重连将有60秒的等待时间",2, '_bemfa')
                    extra_log(rf"等待60秒...",2, '_bemfa')
                    time.sleep(60)
            self.connTCP()
            self.add_send_heartbeat_packet_job()
            self.add_update_bemfa_job()
            self.mainloop()
            self.run(retry=True)