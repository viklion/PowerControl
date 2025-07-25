import yaml, json, os, time, socket, subprocess, requests, shutil, threading
from datetime import datetime, timedelta
from wakeonlan import send_magic_packet
from pythonping import ping
from serverchan_sdk import sc_send
from apscheduler.schedulers.background import BackgroundScheduler

class PCfuncs():
    start_time = time.time()
    yaml_file = 'config.yaml'
    yaml_path = os.path.join(os.getcwd(), 'data', yaml_file)
    default_path = os.path.join(os.getcwd(), 'default', yaml_file)
    log_path = os.path.join(os.getcwd(), 'data', 'logs')
    pc_state = []

    def __init__(self):
        self.yaml_changed = False
        self.is_power_off = False
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # 检查目录权限
        self.check_permission('r')
        self.check_permission('w')

        # 检查是否存在配置文件，没有则拷贝一份
        self.check_yaml()

        # 读取配置文件
        yd = self.read_config_yaml()

        # 读取默认配置文件
        yd_default = self.read_default_yaml()

        # 更新YAML
        self.update_yaml(yd ,yd_default)
        if self.yaml_changed:
            self.write_config_yaml(yd)
            p_print('配置文件已更新新内容')

        # 读取参数
        PCfuncs.version = get_version()
        PCfuncs.bemfa_enabled = checkbool(yd['bemfa']['enabled'])
        if PCfuncs.bemfa_enabled:
            PCfuncs.bemfa_uid = trans_str(yd['bemfa']['uid'])
            PCfuncs.bemfa_topic = trans_str(yd['bemfa']['topic'])
        PCfuncs.device_name = trans_str(yd['devices']['name'])
        PCfuncs.device_ip = trans_str(yd['devices']['ip'])
        PCfuncs.wol_enabled = checkbool(yd['devices']['wol']['enabled'])
        if PCfuncs.wol_enabled:
            PCfuncs.wol_method_wakeonlan = checkbool(yd['devices']['wol']['method']['wakeonlan'])
            PCfuncs.wol_method_shell = checkbool(yd['devices']['wol']['method']['shell'])
            if PCfuncs.wol_method_wakeonlan:
                PCfuncs.wol_mac = trans_str(yd['devices']['wol']['mac'])
                PCfuncs.wol_destination = trans_str(yd['devices']['wol']['destination'])
                PCfuncs.wol_port = int(yd['devices']['wol']['port'])
                PCfuncs.wol_interface = trans_str(yd['devices']['wol']['interface']).lower()
            elif PCfuncs.wol_method_shell:
                PCfuncs.wol_shell_script = trans_str(yd['devices']['wol']['shell_script'])
        PCfuncs.shutdown_enabled = checkbool(yd['devices']['shutdown']['enabled'])
        if PCfuncs.shutdown_enabled:
            PCfuncs.shutdown_method_netrpc = checkbool(yd['devices']['shutdown']['method']['netrpc'])
            PCfuncs.shutdown_method_udp = checkbool(yd['devices']['shutdown']['method']['udp'])
            PCfuncs.shutdown_method_shell = checkbool(yd['devices']['shutdown']['method']['shell'])
            PCfuncs.shutdown_time = trans_str(yd['devices']['shutdown']['time'])
            if PCfuncs.shutdown_method_netrpc:
                PCfuncs.shutdown_pc_account = trans_str(yd['devices']['shutdown']['account'])
                PCfuncs.shutdown_pc_password = trans_str(yd['devices']['shutdown']['password'])
            elif PCfuncs.shutdown_method_shell:
                PCfuncs.shutdown_shell_script = trans_str(yd['devices']['shutdown']['shell_script'])
            PCfuncs.shutdown_timeout = int(yd['devices']['shutdown']['timeout'])
        PCfuncs.ping_enabled = checkbool(yd['devices']['ping']['enabled'])
        if PCfuncs.ping_enabled:
            PCfuncs.ping_time = int(yd['devices']['ping']['time'])
            PCfuncs.ping_method_pcping = checkbool(yd['devices']['ping']['method']['pcping'])
            PCfuncs.ping_method_shell = checkbool(yd['devices']['ping']['method']['shell'])
            if PCfuncs.ping_method_shell:
                PCfuncs.ping_shell_script = trans_str(yd['devices']['ping']['shell_script'])
                PCfuncs.ping_on_keyword = trans_str(yd['devices']['ping']['on_keyword'])
                PCfuncs.ping_off_keyword = trans_str(yd['devices']['ping']['off_keyword'])
        PCfuncs.shell_allowed = tuple(yd['devices']['shell_allowed'])
        PCfuncs.log_enabled = checkbool(yd['functions']['log']['enabled'])
        if PCfuncs.log_enabled:
            PCfuncs.log_level = int(yd['functions']['log']['level'])
            PCfuncs.clear_log_enabled = checkbool(yd['functions']['log']['clear_log']['enabled'])
            if PCfuncs.clear_log_enabled:
                PCfuncs.log_keep_days = int(yd['functions']['log']['clear_log']['keep_days'])
        PCfuncs.push_enabled = checkbool(yd['functions']['push_notifications']['enabled'])
        if PCfuncs.push_enabled:
            PCfuncs.push_bemfa_reconnect = checkbool(yd['functions']['push_notifications']['bemfa_reconnect'])
            PCfuncs.push_serverchan_turbo_enabled = checkbool(yd['functions']['push_notifications']['ServerChan_turbo']['enabled'])
            if PCfuncs.push_serverchan_turbo_enabled:
                PCfuncs.push_serverchan_turbo_SendKey = trans_str(yd['functions']['push_notifications']['ServerChan_turbo']['SendKey'])
                PCfuncs.push_serverchan_turbo_channel = trans_str(yd['functions']['push_notifications']['ServerChan_turbo']['channel'])
            PCfuncs.push_serverchan3_enabled = checkbool(yd['functions']['push_notifications']['ServerChan3']['enabled'])
            if PCfuncs.push_serverchan3_enabled:
                PCfuncs.push_serverchan3_SendKey = trans_str(yd['functions']['push_notifications']['ServerChan3']['SendKey'])
            PCfuncs.push_qmsg_enabled = checkbool(yd['functions']['push_notifications']['Qmsg']['enabled'])
            if PCfuncs.push_qmsg_enabled:
                PCfuncs.push_qmsg_key = trans_str(yd['functions']['push_notifications']['Qmsg']['key'])
                PCfuncs.push_qmsg_qq = trans_str(yd['functions']['push_notifications']['Qmsg']['qq'])
            PCfuncs.push_wechat_webhook_enabled = checkbool(yd['functions']['push_notifications']['WeChat_webhook']['enabled'])
            if PCfuncs.push_wechat_webhook_enabled:
                PCfuncs.push_wechat_webhook_url = trans_str(yd['functions']['push_notifications']['WeChat_webhook']['url'])

        # 本机ip
        PCfuncs.local_ip = get_ip_address()

        # 判断处理参数
        if PCfuncs.device_name:
            PCfuncs.device_name = f'[{PCfuncs.device_name}]'
        if PCfuncs.wol_method_wakeonlan:
            if PCfuncs.wol_destination == 'broadcast_ip_global':
                PCfuncs.wol_destination = '255.255.255.255'
            elif PCfuncs.wol_destination == 'broadcast_ip_direct':
                PCfuncs.wol_destination = PCfuncs.device_ip.rsplit('.', 1)[0] + '.255'
            elif PCfuncs.wol_destination == 'device_ip':
                PCfuncs.wol_destination = PCfuncs.device_ip
            if PCfuncs.wol_interface == 'default':
                PCfuncs.wol_interface = PCfuncs.local_ip
            elif PCfuncs.wol_interface == 'none':
                PCfuncs.wol_interface = None

        print_and_log('----------------------------------', 2)
        print_and_log('PowerControl启动', 2)
        send_message('PowerControl启动')
        if self.yaml_changed:
            write_log('配置文件已更新新内容', 2)
        print_and_log('获取本机ip：'+ PCfuncs.local_ip, 2)

        # 启动定时任务
        self.add_ping_job()
        self.add_clear_log_job()

    # 检查目录权限
    def check_permission(self, mode):
        path = os.path.join(os.getcwd(), 'data')
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

    # 检查YAML文件
    def check_yaml(self):
        # 检查当前目录下是否存在yaml文件
        if not os.path.isfile(self.yaml_path):
            try:
                # 从default目录拷贝文件到当前目录
                shutil.copy(self.default_path, self.yaml_path)
                p_print(f"已生成'{self.yaml_file}'")
            except Exception as e:
                p_print(f"生成'{self.yaml_file}'失败: {e}")
        else:
            p_print(f"'{self.yaml_file}'存在")

    # 读取用户YAML文件
    def read_config_yaml(self):
        try:
            with open(self.yaml_path, 'r',encoding='GBK') as f:
                return yaml.safe_load(f)
        except Exception as e:
            p_print("读取配置文件出错:" + str(e))
            return {}
    # 读取默认YAML文件
    def read_default_yaml(self):
        try:
            with open(self.default_path, 'r',encoding='GBK') as f:
                return yaml.safe_load(f)
        except Exception as e:
            p_print(str(e))
            return {}

    # 更新YAML文件
    def update_yaml(self ,config_yaml ,default_yaml):
        try:
            for key, value in default_yaml.items():
                if key in config_yaml:
                    if isinstance(value, dict):
                        if isinstance(config_yaml[key], dict):
                            # 如果两个值都是字典，则递归合并
                            self.update_yaml(config_yaml[key], value)
                        else:
                            # 如果原yaml中的值不是字典，则更新为默认值
                            config_yaml[key] = value
                            self.yaml_changed = True
                else:
                    # 如果键在原yaml中不存在，则添加该键
                    config_yaml[key] = value
                    self.yaml_changed = True
        except Exception as e:
            p_print("更新配置文件出错:" + str(e))
            self.yaml_changed = False

    # 保存YAML文件
    def write_config_yaml(self ,data):
        try:
            with open(self.yaml_path, 'w',encoding='GBK') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            p_print("保存配置文件成功")
            return True
        except Exception as e:
            p_print("保存配置文件出错:" + str(e))
            return str(e)

    # 定时ping检测设备状态
    def ping_check(self ,is_power_off):
        try:
            ping_result = pcping()
            write_log('\n' + ping_result + '\n' + '----------------------------------', 1 ,'_ping')
            if 'Reply' in ping_result or 'receive on' in ping_result:
                is_power_off = False
                new_state = ["在线","on"]
            elif 'timed out' in ping_result or 'receive off' in ping_result:
                if not is_power_off:
                    self.ping_check(True)
                    return
                new_state = ["离线","off"]
            else:
                new_state = ["未知","unknown"]
            if self.pc_state != new_state:
                self.pc_state = new_state
                print_and_log(f"设备状态更新：{self.pc_state[0]}",2)
                send_message(f"状态更新：{self.pc_state[0]}")
        except Exception as e:
            extra_log("ping出错：" + str(e),3,'_ping')

    # 开启定时ping
    def add_ping_job(self):
        if self.ping_enabled:
            try:
                self.scheduler.add_job(self.ping_check, 'interval', seconds=self.ping_time, args=(self.is_power_off,) ,next_run_time=datetime.now(), id='ping_job')
                print_and_log("Ping服务已启动", 2)
            except Exception as e:
                print_and_log("启动定时ping任务出错：" + str(e),3)

    # 开启定时清理日志
    def add_clear_log_job(self):
        if self.log_enabled:
            if self.clear_log_enabled:
                try:
                    self.scheduler.add_job(clear_log, 'cron', hour=12, next_run_time=datetime.now(), id='clear_log_job')
                    print_and_log("日志定时清理已启动(每天中午12点)", 2)
                except Exception as e:
                    print_and_log("启动定时清理日志任务出错：" + str(e),3)

    # 统计运行时间
    def run_time(self):
        run_timedelta = timedelta(seconds=time.time()-self.start_time)
        # 获取天、小时、分钟和秒
        days = run_timedelta.days
        hours, remainder = divmod(run_timedelta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"已运行：{days}天{hours}小时{minutes}分钟{seconds}秒"

#---------------------------------------------------------------------------------------------------------
# 获取当前时间
def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

# 读取版本信息
def get_version():
    try:
        version = str(os.getenv('VERSION', '版本号未知'))
        return f"V{version}"
    except:
        return "版本号获取失败"

# 带时间的print
def p_print(content):
    print(get_time() + ' ' +content)

# 返回布尔值
def checkbool(bool_str):
    return str(bool_str).lower() == 'true'

# 转变字符串并去掉空格
def trans_str(thing):
    if thing is None:
        return ''
    return str(thing).strip()

# 日志记录
def write_log(content, level, nameadd = ''):
    if PCfuncs.log_enabled:
        if PCfuncs.log_level == 1 or level >= PCfuncs.log_level:
            try:
                if not os.path.exists(PCfuncs.log_path):
                    # 如果不存在，则创建logs文件夹
                    os.makedirs(PCfuncs.log_path)
                # 打开日志文件，"a"追加写入
                time_day = datetime.now().strftime('%Y-%m-%d')
                with open(os.path.join(PCfuncs.log_path ,rf'{time_day}{nameadd}.log'), 'a',encoding='GBK') as file:
                    if level == 1:
                        front = '[Result]: '
                    elif level == 2:
                        front = '[Status]: '
                    elif level == 3:
                        front = '[Error]: '
                    file.write(PCfuncs.device_name + front + get_time() + '  ' + content + '\n')
            except Exception as e:
                p_print(get_time() + " 写入日志出错了：\n" + str(e))

# 清理日志
def clear_log():
    if os.path.exists(PCfuncs.log_path):
        keep_days = PCfuncs.log_keep_days
        # 获取今天的日期
        today = datetime.today()
        # 需要保留的最早日期
        if keep_days == 0:  # 只保留当天日志
            keep_date = datetime(today.year, today.month, today.day)
        else:
            keep_date = today - timedelta(days=keep_days)
        # 遍历日志目录
        for filename in os.listdir(PCfuncs.log_path):
            # 只处理.log文件
            if filename.endswith(".log"):
                try:
                    # 获取文件的完整路径
                    file_path = os.path.join(PCfuncs.log_path, filename)
                    # 获取文件的最后修改时间
                    file_mtime = os.path.getmtime(file_path)
                    # 将最后修改时间转换为 datetime 对象
                    file_date = datetime.fromtimestamp(file_mtime)
                    # 对比日期，删除早于保留日期的文件
                    if file_date < keep_date:
                        os.remove(file_path)
                        print_and_log(f"已自动删除日志: {filename}", 2)
                except Exception as e:
                    # 如果发生异常输出错误信息
                    print_and_log(f"删除日志 {filename} 出错: {str(e)}", 3)

# 同时打印和日志记录
def print_and_log(content, level):
    p_print(content)
    write_log(content, level)

# 扩展日志记录
def extra_log(content, level, nameadd):
    print_and_log(content,level)
    write_log(content,1, nameadd)

# 消息推送
def send_message(title, desp='', retry=False):
    if PCfuncs.push_enabled:
        if not retry:
            send = threading.Thread(target=send_message_main, args=(title, desp,))
            send.start()
        elif retry:
            re_send = threading.Thread(target=re_send_message_main, args=(title, desp,))
            re_send.start()
def send_message_main(title, desp=''):
    response = {}
    if PCfuncs.push_enabled:
        response['serverchan_turbo'] = send_message_serverchan_turbo(title, desp)
        response['serverchan3'] = send_message_serverchan3(title, desp)
        response['qmsg'] = send_message_qmsg(title, desp)
        response['wechat_webhook'] = send_message_wechat_webhook(title, desp)
    return response

# 断网下等待网络恢复重新发送
def re_send_message_main(title, desp):
    while True:
        try:
            rs = str(ping('www.baidu.com', timeout = 1, count = 1))
        except:
            time.sleep(10)
            continue
        if 'timed out' in rs:
            time.sleep(10)
            continue
        elif 'Reply' in rs:
            send_message(title, desp)
            break

# Server酱Turbo推送
def send_message_serverchan_turbo(title, desp=''):
    if PCfuncs.push_serverchan_turbo_enabled:
        try:
            data = {
                    'title': PCfuncs.device_name + title,
                    'desp': get_time() + ' ' + desp,
                    'channel': PCfuncs.push_serverchan_turbo_channel
                }
            rs = requests.post(f'https://sctapi.ftqq.com/{PCfuncs.push_serverchan_turbo_SendKey}.send', data=data).json()
            write_log("Server酱Turbo推送返回:" + str(rs), 1, '_message')
            return rs
        except Exception as e:
            rs = str(e)
            print_and_log("Server酱Turbo推送消息出错", 3)
            write_log("Server酱Turbo推送消息出错：" + rs, 1, '_message')
            return rs

# Server酱3推送
def send_message_serverchan3(title, desp=''):
    if PCfuncs.push_serverchan3_enabled:
        try:
            rs = sc_send(f"{PCfuncs.push_serverchan3_SendKey}", PCfuncs.device_name + title, get_time() + ' ' + desp, {"tags": "PowerControl"})
            write_log("Server酱3推送返回:" + str(rs), 1, '_message')
            return rs
        except Exception as e:
            rs = str(e)
            print_and_log("Server酱3推送消息出错", 3)
            write_log("Server酱3推送消息出错：" + rs, 1, '_message')
            return rs

# Qmsg酱推送
def send_message_qmsg(title, desp=''):
    if PCfuncs.push_qmsg_enabled:
        try:
            data = {
                    'msg': PCfuncs.device_name + title + '\n' + get_time() + ' ' + desp,
                    'qq': PCfuncs.push_qmsg_qq
                }
            rs = requests.post(f'https://qmsg.zendee.cn/send/{PCfuncs.push_qmsg_key}', data=data).json()
            # 移除 'ad' 广告字段
            if 'ad' in rs:
                del rs['ad']
            write_log("Qmsg酱推送返回:" + str(rs), 1, '_message')
            return rs
        except Exception as e:
            rs = str(e)
            print_and_log("Qmsg酱推送消息出错", 3)
            write_log("Qmsg酱推送消息出错：" + rs, 1, '_message')
            return rs

# 企业微信群机器人推送
def send_message_wechat_webhook(title, desp=''):
    if PCfuncs.push_wechat_webhook_enabled:
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                    'msgtype': 'text',
                    'text': {
                        'content': f'{PCfuncs.device_name}{title}\n{get_time()} {desp}',
                        },
                }
            rs = requests.post(PCfuncs.push_wechat_webhook_url, json=data, headers=headers).json()
            write_log("企业微信群机器人推送返回:" + str(rs), 1, '_message')
            return rs
        except Exception as e:
            rs = str(e)
            print_and_log("企业微信群机器人推送消息出错", 3)
            write_log("企业微信群机器人推送消息出错：" + rs, 1, '_message')
            return rs

# 关机
def pcshutdown():
    if PCfuncs.shutdown_enabled:
        if PCfuncs.shutdown_method_netrpc:
            try:
                # 构建命令
                command = [
                    "net", "rpc", "shutdown",
                    "-f", "-t", PCfuncs.shutdown_time, "-C", f"设备将于{PCfuncs.shutdown_time}秒后关闭",
                    "-U", f"{PCfuncs.shutdown_pc_account}%{PCfuncs.shutdown_pc_password}", "-I", PCfuncs.device_ip
                ]
                # 使用 subprocess.run() 执行命令并获取输出
                result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=PCfuncs.shutdown_timeout)
                return result.stdout.replace('\n', '').replace('\r', '')
            except Exception as e:
                return str(e)
        elif PCfuncs.shutdown_method_udp:
            try:
                # 创建一个UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # 设置超时时间
                sock.settimeout(PCfuncs.shutdown_timeout)
                # 目标主机和端口
                host = PCfuncs.device_ip
                port = 17678
                # 要发送的消息
                data = {
                    'cmd': 'shutdown',
                    'time': PCfuncs.shutdown_time,
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
        elif PCfuncs.shutdown_method_shell:
            if PCfuncs.shutdown_shell_script.startswith(PCfuncs.shell_allowed):
                try:
                    # 执行并获取shell命令的结果
                    result = subprocess.run(PCfuncs.shutdown_shell_script, shell=True, capture_output=True, text=True, check=True, timeout=max(PCfuncs.shutdown_timeout, 5))
                    if result.stdout:
                        return 'succeeded:' + result.stdout.replace("\n", "→")
                    else:
                        return 'succeeded: 已发送指令'
                except subprocess.TimeoutExpired as e:
                    # 处理sshpass超时但已经成功执行的报错
                    if 'sshpass' in PCfuncs.shutdown_shell_script:
                        return 'succeeded: 已发送指令'
                    else:
                        return str(e).replace("\n", "→")
                except subprocess.CalledProcessError as e:
                    # 捕获并返回subprocess错误输出
                    return f"Error: {e.stderr.replace("\n", "→")}"
                except Exception as e:
                    return str(e).replace("\n", "→")
            else:
                return "Error:不允许的指令"
    return None

# 网络唤醒
def pcwol():
    if PCfuncs.wol_enabled:
        if PCfuncs.wol_method_wakeonlan:
            try:
                # 唤醒设备
                send_magic_packet(PCfuncs.wol_mac, ip_address = PCfuncs.wol_destination, port = PCfuncs.wol_port, interface = PCfuncs.wol_interface)
                return 'done'
            except Exception as e:
                return str(e).replace("\n", "→")
        elif PCfuncs.wol_method_shell:
            if PCfuncs.wol_shell_script.startswith(PCfuncs.shell_allowed):
                try:
                    # 执行并获取shell命令的结果
                    result = subprocess.run(PCfuncs.wol_shell_script, shell=True, capture_output=True, text=True, check=True, timeout=5)
                    if result.stdout:
                        return 'done: ' + result.stdout.replace("\n", "→")
                    else:
                        return 'done: 已发送指令'
                except subprocess.TimeoutExpired as e:
                    # 处理sshpass超时但已经成功执行的报错
                    if 'sshpass' in PCfuncs.wol_shell_script:
                        return 'done: 已发送指令'
                    else:
                        return str(e).replace("\n", "→")
                except subprocess.CalledProcessError as e:
                    # 捕获并返回subprocess错误输出
                    return f"Error: {e.stderr.replace("\n", "→")}"
                except Exception as e:
                    return str(e).replace("\n", "→")
            else:
                return "Error:不允许的指令"
    return None

# ping
def pcping():
    if PCfuncs.ping_enabled:
        if PCfuncs.ping_method_pcping:
            # ping设备
            return str(ping(PCfuncs.device_ip, timeout = 1, count = 1)).replace('\r\n', '→').replace('→→', ' → ')
        elif PCfuncs.ping_method_shell:
            if PCfuncs.ping_shell_script.startswith(PCfuncs.shell_allowed):
                try:
                    # 执行并获取shell命令的结果
                    result = subprocess.run(PCfuncs.ping_shell_script, shell=True, capture_output=True, text=True, check=False, timeout=2)
                    if PCfuncs.ping_on_keyword in result.stdout:
                        return 'receive on：' + result.stdout.replace("\n", "→")
                    elif PCfuncs.ping_off_keyword in result.stdout:
                        return 'receive off：' + result.stdout.replace("\n", "→")
                    else:
                        return 'receive unknown：' + result.stdout.replace("\n", "→")
                except subprocess.TimeoutExpired as e:
                    return 'timed out：' + str(e).replace("\n", "→")
                except subprocess.CalledProcessError as e:
                    # 捕获并返回subprocess错误输出
                    return f"Error: {e.stderr.replace("\n", "→")}"
                except Exception as e:
                    return str(e).replace("\n", "→")
            else:
                return "Error:不允许的指令"