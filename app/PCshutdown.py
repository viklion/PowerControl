import socket, json, subprocess, os
from time import sleep
from win11toast import toast

def get_ip_address():
    try:
        # 创建一个socket对象
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到目标网址
        s.connect(("192.168.255.255", 80))
        # 获取本地IP地址
        ip_address = s.getsockname()[0]
        # 关闭socket连接
        s.close()
        return ip_address
    except:
        sleep(10)
        get_ip_address()

def ptoast(title,text):
    try:
        toast(title,text)
    except:
        pass

UDP_IP = get_ip_address() # 自动获取本地ip地址
UDP_PORT = 17678 # 接收端口

try:
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind(('0.0.0.0', UDP_PORT))
    ptoast("PCshutdown已启动",f"本机ip：{UDP_IP}，监听端口：{UDP_PORT}，将保持后台运行")
except Exception as e:
    ptoast("PCshutdown已退出","启动失败：" + str(e))
    os._exit(0)

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        # 将接收到的数据解码并反序列化
        json_data = data.decode()
        received_data = json.loads(json_data)
        if received_data['cmd'] == "shutdown":
            subprocess.Popen(['shutdown', '-s', '-t', str(received_data['time'])], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sent = sock.sendto('succeeded'.encode('utf-8'), addr)
    except Exception as e:
        sent = sock.sendto('failed'.encode('utf-8'), addr)
        ptoast("PCshutdown命令执行失败","error：" + str(e))
        continue

