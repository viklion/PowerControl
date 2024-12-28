import yaml
import json
import os
from datetime import datetime, timedelta
import time
import socket
import subprocess
from wakeonlan import send_magic_packet
import requests
import shutil
from pythonping import ping
from serverchan_sdk import sc_send

# 检查YAML文件
def check_yaml():
    # 检查当前目录下是否存在yaml文件
    if not os.path.isfile(yaml_path):
        try:
            # 从default目录拷贝文件到当前目录
            shutil.copy(default_path, yaml_path)
            p_print(f"已生成'{yaml_file}'")
        except Exception as e:
            p_print(f"生成'{yaml_file}'失败: {e}")
    else:
        p_print(f"'{yaml_file}'存在")

# YAML路径
def get_yaml_path():
    return yaml_path

# 读取YAML文件
def read_config_yaml():
    try:
        with open(yaml_path, 'r',encoding='GBK') as f:
            return yaml.safe_load(f)
    except Exception as e:
        p_print("读取配置文件出错:" + str(e))
        return {}
def read_default_yaml():
    try:
        with open(default_path, 'r',encoding='GBK') as f:
            return yaml.safe_load(f)
    except Exception as e:
        p_print(str(e))
        return {}

# 保存YAML文件
def write_config_yaml(data):
    try:
        with open(yaml_path, 'w',encoding='GBK') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        p_print("保存配置文件成功")
        return True
    except Exception as e:
        p_print("保存配置文件出错:" + str(e))
        return str(e)

# 更新YAML文件
def update_yaml(config_yaml, default_yaml):
    global yaml_changed
    try:
        for key, value in default_yaml.items():
            if key in config_yaml:
                if isinstance(value, dict):
                    if isinstance(config_yaml[key], dict):
                        # 如果两个值都是字典，则递归合并
                        update_yaml(config_yaml[key], value)
                    else:
                        # 如果原yaml中的值不是字典，则更新为默认值
                        config_yaml[key] = value
                        yaml_changed = True
            else:
                # 如果键在原yaml中不存在，则添加该键
                config_yaml[key] = value
                yaml_changed = True
    except Exception as e:
        p_print("更新配置文件出错:" + str(e))
        yaml_changed = False

# 检查目录权限
def check_permission(mode, folder):
    path = os.path.join(os.getcwd(), folder)
    # 检查目录是否存在
    if not os.path.exists(path):
        p_print(f"{path} 不存在")
        
    if mode == 'r':
        # 检查目录是否可读
        if os.access(path, os.R_OK):
            p_print(f"{path} 有读取权限")
        else:
            p_print(f"{path} 无读取权限")
    elif mode == 'w':
        # 检查目录是否可写
        if os.access(path, os.W_OK):
            p_print(f"{path} 有写入权限")
        else:
            p_print(f"{path} 无写入权限")
    elif mode == 'x':
        # 检查目录是否可执行
        if os.access(path, os.X_OK):
            p_print(f"{path} 有执行权限")
        else:
            p_print(f"{path} 无执行权限")

# 返回布尔值
def checkbool(bool_str):
    return str(bool_str).lower() == 'true'

# 转变字符串并去掉空格
def trans_str(thing):
    if thing is None:
        return ''
    return str(thing).strip()

# 返回变量
def get_var(var):
    return globals()[var]

# 获取当前时间
def get_time():
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return time_now

# 获取本机ip地址
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
    except socket.error:
        return "无法获取IP地址"
def return_ip():
    return local_ip

# 关机
def pcshutdown():
    if shutdown_enabled:
        if method_netrpc:
            try:
                # 构建命令
                command = [
                    "net", "rpc", "shutdown",
                    "-f", "-t", shutdown_time, "-C", f"设备将于{shutdown_time}秒后关闭",
                    "-U", f"{pc_account}%{pc_password}", "-I", device_ip
                ]
                # 使用 subprocess.run() 执行命令并获取输出
                result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=2)
                return result.stdout
            except Exception as e:
                return str(e)
        elif method_udp:
            try:
                # 创建一个UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # 设置超时时间
                sock.settimeout(3)
                # 目标主机和端口
                host = device_ip
                port = 17678
                # 要发送的消息
                data = {
                    'cmd': 'shutdown',
                    'time': shutdown_time,
                }
                # 将字典序列化为JSON字符串
                json_data = json.dumps(data)
                # 发送数据
                _ = sock.sendto(json_data.encode(),(host, port))
                # 接收响应
                response, _ = sock.recvfrom(1024)
                return response.decode('utf-8')
            except Exception as e:
                return str(e)
            finally:
                # 关闭socket
                sock.close()
    return None

# 网络唤醒
def pcwol():
    if wol_enabled:
        try:
            # 唤醒设备
            send_magic_packet(pc_mac,  interface = local_ip)
            return True
        except Exception as e:
            return str(e)
    return None
        
# ping
def pcping():
    # ping设备
    ping_result = str(ping(device_ip, timeout = 1, count = 1))
    return ping_result

# 日志记录
def write_log(content, level, nameadd = ''):
    if log_enabled:
        if log_level == 1 or level >= log_level:
            try:
                if not os.path.exists(os.path.join('data', 'logs')):
                    # 如果不存在，则创建logs文件夹
                    os.makedirs(os.path.join('data', 'logs'))
                # 打开日志文件，"a"追加写入
                time_day = datetime.now().strftime('%Y-%m-%d')
                with open(os.path.join('data', 'logs' ,rf'{time_day}{nameadd}.log'), 'a',encoding='GBK') as file:
                    if level == 1:
                        front = '[Result]: '
                    elif level == 2:
                        front = '[Status]: '
                    elif level == 3:
                        front = '[Error]: '
                    file.write(device_name + front + get_time() + '  ' + content + '\n')
            except Exception as e:
                p_print(get_time() + " 写入日志出错了：\n" + str(e))

# 消息推送
def send_message(content):
    if push_enabled:
        if push_serverchan_turbo_enabled:
            try:
                data = {
                        'title': device_name + content,
                        'desp': get_time(),
                        'channel': push_serverchan_turbo_channel
                    }
                _ = requests.post(f'https://sctapi.ftqq.com/{push_serverchan_turbo_SendKey}.send', data=data)
            except Exception as e:
                p_print("Server酱Turbo发送消息出错：" + str(e))
        if push_serverchan3_enabled:
            try:
                _ = sc_send(f"{push_serverchan3_SendKey}", device_name + content, get_time(), {"tags": "PowerControl"})
            except Exception as e:
                p_print("Server酱3发送消息出错：" + str(e))
        if push_qmsg_enabled:
            try:
                data = {
                        'msg': device_name + content + '\n' + get_time(),
                        'qq': push_qmsg_qq
                    }
                _ = requests.post(f'https://qmsg.zendee.cn/send/{push_qmsg_key}', data=data)
            except Exception as e:
                p_print("Qmsg酱发送消息出错：" + str(e))

# 带时间的print
def p_print(content):
    print(get_time() + ' ' +content)

# 同时打印和日志记录
def print_and_log(content, level):
    p_print(content)
    write_log(content, level)

# 统计运行时间
def run_time():
    run_timedelta = timedelta(seconds = time.time() - start_time)
    # 获取天、小时、分钟和秒
    days = run_timedelta.days
    hours, remainder = divmod(run_timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"已运行：{days}天{hours}小时{minutes}分钟{seconds}秒"
    


#--------------------------------------------------------------------
#初始化
start_time = time.time()
yaml_file = 'config.yaml'
yaml_path = os.path.join(os.getcwd(), 'data', yaml_file)
default_path = os.path.join(os.getcwd(), 'default', yaml_file)
yaml_changed = False

#检查目录权限
check_permission('r','data')
check_permission('w','data')

#检查是否存在配置文件，没有则拷贝一份
check_yaml()

#读取配置文件
yd = read_config_yaml()

#读取默认配置文件
yd_default = read_default_yaml()

#更新YAML
update_yaml(yd ,yd_default)
if yaml_changed:
    write_config_yaml(yd)
    p_print("配置文件已更新新内容")

#参数
bemfa_enabled = checkbool(yd['bemfa']['enabled'])
if bemfa_enabled:
    bemfa_uid = trans_str(yd['bemfa']['uid'])
    bemfa_topic = trans_str(yd['bemfa']['topic'])
device_name = trans_str(yd['devices']['name'])
if device_name:
    device_name = f'[{device_name}]'
wol_enabled = checkbool(yd['devices']['wol']['enabled'])
if wol_enabled:
    pc_mac = trans_str(yd['devices']['wol']['mac'])
shutdown_enabled = checkbool(yd['devices']['shutdown']['enabled'])
if shutdown_enabled:
    method_netrpc = checkbool(yd['devices']['shutdown']['method']['netrpc'])
    method_udp = checkbool(yd['devices']['shutdown']['method']['udp'])
    shutdown_time = trans_str(yd['devices']['shutdown']['time'])
    if method_netrpc:
        pc_account = trans_str(yd['devices']['shutdown']['account'])
        pc_password = trans_str(yd['devices']['shutdown']['password'])
ping_enabled = checkbool(yd['devices']['ping']['enabled'])
if ping_enabled:
    ping_time = int(yd['devices']['ping']['time'])
if shutdown_enabled or ping_enabled:
    device_ip = trans_str(yd['devices']['ip'])
log_enabled = checkbool(yd['functions']['log']['enabled'])
if log_enabled:
    log_level = int(yd['functions']['log']['level'])
push_enabled = checkbool(yd['functions']['push_notifications']['enabled'])
if push_enabled:
    push_serverchan_turbo_enabled = checkbool(yd['functions']['push_notifications']['ServerChan_turbo']['enabled'])
    if push_serverchan_turbo_enabled:
        push_serverchan_turbo_SendKey = trans_str(yd['functions']['push_notifications']['ServerChan_turbo']['SendKey'])
        push_serverchan_turbo_channel = trans_str(yd['functions']['push_notifications']['ServerChan_turbo']['channel'])
    push_serverchan3_enabled = checkbool(yd['functions']['push_notifications']['ServerChan3']['enabled'])
    if push_serverchan3_enabled:
        push_serverchan3_SendKey = trans_str(yd['functions']['push_notifications']['ServerChan3']['SendKey'])
    push_qmsg_enabled = checkbool(yd['functions']['push_notifications']['Qmsg']['enabled'])
    if push_qmsg_enabled:
        push_qmsg_key = trans_str(yd['functions']['push_notifications']['Qmsg']['key'])
        push_qmsg_qq = trans_str(yd['functions']['push_notifications']['Qmsg']['qq'])


print_and_log('PowerControl启动', 2)
send_message('PowerControl启动')
#本机ip
local_ip = get_ip_address()
print_and_log('获取本机ip：'+local_ip, 2)

del yd
del yd_default