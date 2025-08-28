# PCfunctions.py
import os
import time
import socket
import json
import subprocess
from wakeonlan import send_magic_packet
from pythonping import ping
from datetime import datetime, timedelta
from PCdata import PCdata

class PCfuncs():
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """限制只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 只初始化一次
        if self._initialized:
            return
        self._initialized = True
        # 全局数据存储
        self.PC_data = PCdata()
        self.PC_logger = self.PC_data.get_main_logger()
    
    # 获取当前时间
    @staticmethod
    def get_time():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 获取本机ip地址
    def get_ip_address(self):
        try:
            # 创建一个socket对象
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接到目标网址
            s.connect(("119.29.29.29", 80))
            # 获取本地IP地址
            ip_address = s.getsockname()[0]
            # 关闭socket连接
            s.close()
            self.PC_logger.info(f"获取本机IP地址: {ip_address}")
            return ip_address
        except socket.error:
            self.PC_logger.error("无法获取IP地址")
            return "无法获取IP地址"

    # 版本信息
    def get_version(self):
        return f'V{self.PC_data.get_main_VERSION()}'

    # 清理bemfa重连消息推送次数统计
    def clear_bemfa_reconnect_message_count(self):
        self.PC_data.update(['main', 'bemfa_reconnect_message_count'], 0)

    # 返回布尔值
    @staticmethod
    def checkbool(bool_str):
        return str(bool_str).lower() == 'true'

    # 转变字符串并去掉空格
    @staticmethod
    def trans_str(thing):
        if thing is None:
            return ''
        return str(thing).strip()

    # 检查目录权限
    def check_permission(self, path, mode):
        # 检查目录是否存在
        if not os.path.exists(path):
            self.PC_logger.error(f"{path} 不存在")
            return False

        if mode == 'r':
            # 检查目录是否可读
            if os.access(path, os.R_OK):
                self.PC_logger.debug(f"{path} 有读取权限")
                return True
            else:
                self.PC_logger.error(f"{path} 无读取权限")
                return False
        elif mode == 'w':
            # 检查目录是否可写
            if os.access(path, os.W_OK):
                self.PC_logger.debug(f"{path} 有写入权限")
                return True
            else:
                self.PC_logger.error(f"{path} 无写入权限")
                return False
        elif mode == 'x':
            # 检查目录是否可执行
            if os.access(path, os.X_OK):
                self.PC_logger.debug(f"{path} 有执行权限")
                return True
            else:
                self.PC_logger.error(f"{path} 无执行权限")
                return False

    # 统计运行时间
    def run_time(self):
        run_timedelta = timedelta(seconds=time.time()-self.PC_data.get_main_start_time())
        # 获取天、小时、分钟和秒
        days = run_timedelta.days
        hours, remainder = divmod(run_timedelta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"已运行：{days}天{hours}小时{minutes}分钟{seconds}秒"

    # 清理日志
    def remove_log(self):
        log_dir = os.path.join('data', 'logs')
        if os.path.exists(log_dir):
            keep_days = int(self.PC_data.get_main_yaml_log_days())
            # 获取今天的日期
            today = datetime.today()
            # 需要保留的最早日期
            if keep_days == 0:  # 只保留当天日志
                keep_date = datetime(today.year, today.month, today.day)
            else:
                keep_date = today - timedelta(days=keep_days)
            # 遍历日志目录
            for filename in os.listdir(log_dir):
                # 只处理.log文件
                if filename.endswith(".log"):
                    try:
                        # 获取文件的完整路径
                        file_path = os.path.join(log_dir, filename)
                        # 获取文件的最后修改时间
                        file_mtime = os.path.getmtime(file_path)
                        # 将最后修改时间转换为 datetime 对象
                        file_date = datetime.fromtimestamp(file_mtime)
                        # 对比日期，删除早于保留日期的文件
                        if file_date < keep_date:
                            os.remove(file_path)
                            self.PC_logger.info(f"已自动清理日志: {filename}")
                    except Exception as e:
                        # 如果发生异常输出错误信息
                        self.PC_logger.error(f"自动清理日志 {filename} 出错: {str(e)}")

    # 关机
    def pcshutdown(self, device_id):
        # 设备服务是否启用
        if self.checkbool(self.PC_data.get_device_main_enabled(device_id)) and self.PC_data.get_device_service_thread_is_alive(device_id):
            # 设备是否启用关机功能
            if self.checkbool(self.PC_data.get_device_device_shutdown_enabled(device_id)):
                device_ip = self.PC_data.get_device_device_ip(device_id)
                shutdown_time = self.trans_str(self.PC_data.get_device_device_shutdown_time(device_id))
                shutdown_timeout = int(self.PC_data.get_device_device_shutdown_timeout(device_id))
                # 判断关机方法
                if self.checkbool(self.PC_data.get_device_device_shutdown_method_netrpc(device_id)):
                    try:
                        shutdown_pc_account = self.PC_data.get_device_device_shutdown_account(device_id)
                        shutdown_pc_password = self.PC_data.get_device_device_shutdown_password(device_id)
                        # 构建命令
                        command = [
                            "net", "rpc", "shutdown",
                            "-f", "-t", shutdown_time, "-C", f"设备将于{shutdown_time}秒后关闭",
                            "-U", f"{shutdown_pc_account}%{shutdown_pc_password}", "-I", device_ip
                        ]
                        # 使用 subprocess.run() 执行命令并获取输出
                        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=shutdown_timeout)
                        return result.stdout.replace('\n', '').replace('\r', '')
                    except Exception as e:
                        return str(e)
                elif self.checkbool(self.PC_data.get_device_device_shutdown_method_udp(device_id)):
                    try:
                        # 创建一个UDP socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        # 设置超时时间
                        sock.settimeout(shutdown_timeout)
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
                elif self.checkbool(self.PC_data.get_device_device_shutdown_method_shell(device_id)):
                    shutdown_shell_script = self.PC_data.get_device_device_shutdown_shell_script(device_id)
                    try:
                        # 执行并获取shell命令的结果
                        result = subprocess.run(shutdown_shell_script, shell=True, capture_output=True, text=True, check=True, timeout=max(shutdown_timeout, 5))
                        if result.stdout:
                            return 'succeeded:' + result.stdout.replace("\n", "→")
                        else:
                            return 'succeeded: 已发送指令'
                    except subprocess.TimeoutExpired as e:
                        # 处理sshpass超时但已经成功执行的报错
                        if 'sshpass' in shutdown_shell_script:
                            return 'succeeded: 已发送指令'
                        else:
                            return str(e).replace("\n", "→")
                    except subprocess.CalledProcessError as e:
                        # 捕获并返回subprocess错误输出
                        return f"Error: {e.stderr.replace("\n", "→")}"
                    except Exception as e:
                        return str(e).replace("\n", "→")
            return None
        return None

    # 网络唤醒
    def pcwol(self, device_id):
        # 设备服务是否启用
        if self.checkbool(self.PC_data.get_device_main_enabled(device_id)) and self.PC_data.get_device_service_thread_is_alive(device_id):
            # 网络唤醒是否启用
            if self.checkbool(self.PC_data.get_device_device_wol_enabled(device_id)):
                # 判断唤醒方法
                if self.checkbool(self.PC_data.get_device_device_wol_method_wakeonlan(device_id)):
                    wol_mac = self.PC_data.get_device_device_wol_mac(device_id)
                    wol_port = int(self.PC_data.get_device_device_wol_port(device_id))
                    wol_destination = self.PC_data.get_device_device_wol_destination(device_id)
                    wol_interface = self.PC_data.get_device_device_wol_interface(device_id)
                    device_ip = self.PC_data.get_device_device_ip(device_id)
                    local_ip = self.PC_data.get_main_local_ip()
                    if wol_destination == 'broadcast_ip_global':
                        wol_destination = '255.255.255.255'
                    elif wol_destination == 'broadcast_ip_direct':
                        wol_destination = device_ip.rsplit('.', 1)[0] + '.255'
                    elif wol_destination == 'device_ip':
                        wol_destination = device_ip
                    if wol_interface == 'default':
                        wol_interface = local_ip
                    elif wol_interface == 'none':
                        wol_interface = None
                    try:
                        # 唤醒设备
                        send_magic_packet(wol_mac, ip_address = wol_destination, port = wol_port, interface = wol_interface)
                        return 'done'
                    except Exception as e:
                        return str(e).replace("\n", "→")
                elif self.checkbool(self.PC_data.get_device_device_wol_method_shell(device_id)):
                    wol_shell_script = self.PC_data.get_device_device_wol_shell_script(device_id)
                    try:
                        # 执行并获取shell命令的结果
                        result = subprocess.run(wol_shell_script, shell=True, capture_output=True, text=True, check=True, timeout=5)
                        if result.stdout:
                            return 'done: ' + result.stdout.replace("\n", "→")
                        else:
                            return 'done: 已发送指令'
                    except subprocess.TimeoutExpired as e:
                        # 处理sshpass超时但已经成功执行的报错
                        if 'sshpass' in wol_shell_script:
                            return 'done: 已发送指令'
                        else:
                            return str(e).replace("\n", "→")
                    except subprocess.CalledProcessError as e:
                        # 捕获并返回subprocess错误输出
                        return f"Error: {e.stderr.replace("\n", "→")}"
                    except Exception as e:
                        return str(e).replace("\n", "→")
            return None
        return None

    # ping
    def pcping(self, device_id):
        # 设备服务是否启用
        if self.checkbool(self.PC_data.get_device_main_enabled(device_id)) and self.PC_data.get_device_service_thread_is_alive(device_id):
            # ping是否启用
            if self.checkbool(self.PC_data.get_device_device_ping_enabled(device_id)):
                # 判断ping方法
                if self.checkbool(self.PC_data.get_device_device_ping_method_pcping(device_id)):
                    # ping设备
                    device_ip = self.PC_data.get_device_device_ip(device_id)
                    return str(ping(device_ip, timeout = 1, count = 1)).replace('\r\n', '→').replace('→→', ' → ')
                elif self.checkbool(self.PC_data.get_device_device_ping_method_shell(device_id)):
                    ping_shell_script= self.PC_data.get_device_device_ping_shell_script(device_id)
                    ping_on_keyword= self.PC_data.get_device_device_ping_on_keyword(device_id)
                    ping_off_keyword= self.PC_data.get_device_device_ping_off_keyword(device_id)
                    try:
                        # 执行并获取shell命令的结果
                        result = subprocess.run(ping_shell_script, shell=True, capture_output=True, text=True, check=False, timeout=2)
                        if ping_on_keyword in result.stdout:
                            return 'receive on：' + result.stdout.replace("\n", "→")
                        elif ping_off_keyword in result.stdout:
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
            return None
        return None