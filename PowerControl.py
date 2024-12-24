from pfunctions import pcshutdown,pcwol,print_and_log,send_message,pcping, get_var, write_log
import socket
import threading
import time

class PowerControl():
    def __init__(self):
        self.enabled = get_var('bemfa_enabled')
        if self.enabled:
            self.uid = get_var('bemfa_uid')
            self.topic = get_var('bemfa_topic')
            self.ping_enabled = get_var('ping_enabled')
            if self.ping_enabled:
                self.ping_time = get_var('ping_time')

            self.pc_state = None
            self.ping_check = None
            self.update_bemfa_status = None
            self.update_state = ''

            print_and_log("接入巴法云初始化成功",2)

    #订阅
    def connTCP(self):
        # IP和端口
        server_ip = 'bemfa.com'
        server_port = 8344
        try:
            # 创建socket
            self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 连接服务器
            self.tcp_client_socket.connect((server_ip, server_port))
            # 发送订阅指令
            substr = f'cmd=1&uid={self.uid}&topic={self.topic}\r\n'
            self.tcp_client_socket.send(substr.encode('utf-8'))
            # 写入日志
            print_and_log("巴法云订阅成功", 2)
        except:
            print_and_log("巴法云订阅失败，正在重试", 3)
            time.sleep(2)
            self.connTCP()

    #心跳
    def Ping(self):
        # 发送心跳
        try:
            keeplive = 'ping\r\n'
            self.tcp_client_socket.send(keeplive.encode('utf-8'))
            write_log("已发送心跳",1,'_bemfa')
        except:
            time.sleep(2)
            print_and_log("发送心跳出现问题,重新订阅",3)
            self.connTCP()
        #开启定时，60秒发送一次心跳
        t = threading.Timer(60, self.Ping)
        t.start()

    #定时ping检测设备状态
    def check_state(self, is_power_off):
        try:
            ping_result = pcping()
            write_log('\n' + ping_result + '\n' + '---------------------', 1 ,'_ping_result')
            if 'Reply' in ping_result:
                is_power_off = False
                new_state = "在线"
                self.update_state = "on"
            elif 'timed out' in ping_result:
                if not is_power_off:
                    self.check_state(True)
                    return
                new_state = "离线"
                self.update_state = "off"
            if self.pc_state != new_state:
                self.pc_state = new_state
                print_and_log(f"状态更新：{new_state}",2)
                send_message(f"状态更新：{new_state}")
            #开启ping定时
            self.ping_check = threading.Timer(self.ping_time, self.check_state, args=(is_power_off,))
            self.ping_check.start()
        except Exception as e:
            print_and_log("ping出错：" + str(e),3)

    #定时更新巴法云的设备状态
    def update_bemfa(self):
        if self.update_state:
            substr = f'cmd=2&uid={self.uid}&topic={self.topic}/up&msg={self.update_state}\r\n'
            try:
                self.tcp_client_socket.send(substr.encode("utf-8"))
                write_log("巴法云设备状态更新："+self.update_state, 1, '_bemfa')
            except Exception as e:
                print_and_log("更新巴法云设备状态失败："+str(e),3)
            self.update_bemfa_status = threading.Timer(120, self.update_bemfa)
            self.update_bemfa_status.start()

    #收到消息后执行开关机
    def power_control(self, state):
        if state == 'on' :
            rs = pcwol()
            if rs:
                if rs == True:
                    print_and_log('已发送唤醒指令',2)
                    send_message('已发送唤醒指令')
                else:
                    print_and_log('发送唤醒指令失败：'+ rs ,3)
                    send_message('发送唤醒指令失败')
            else:
                print_and_log('未启用网络唤醒！' ,3)
                send_message('未启用网络唤醒！')
        elif state == 'off':
            rs = pcshutdown()
            if rs:
                if 'succeeded' in rs:
                    print_and_log("已发送关机指令",2)
                    send_message('已发送关机指令')
                else:
                    print_and_log("关机指令发送失败："+ rs ,3)
                    send_message('关机指令发送失败')
            else:
                print_and_log('未启用远程关机！' ,3)
                send_message('未启用远程关机！')

    #启动
    def run(self):
        if self.enabled:
            print_and_log("Bemfa服务启动",2)
            self.connTCP()
            self.Ping()
            if self.ping_enabled:
                print_and_log("Ping服务启动", 2)
                self.check_state(False)
                self.update_bemfa()
            while True:
                try:
                    # 接收服务器发送过来的数据
                    recv_Data = self.tcp_client_socket.recv(1024)
                    recv_str = str(recv_Data.decode('utf-8'))
                    write_log(recv_str,1,'_bemfa')
                except Exception as e:
                    print_and_log("接收巴法服务器消息出错，error: " + str(e), 3)
                    time.sleep(5)
                    continue
                
                if not recv_Data:
                    print_and_log("服务器未返回任何数据，重新订阅",3)
                    self.connTCP()
                
                elif f'uid={self.uid}' in recv_str:
                    #收到开机消息
                    if 'msg=on' in recv_str:
                        self.power_control('on')
                    #收到关机消息
                    elif 'msg=off' in recv_str:
                        self.power_control('off')

if __name__ == '__main__':
    c = PowerControl()
    c.run()