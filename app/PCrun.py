# PCrun.py
import os, threading, time
from PClog import PClog
from PCdata import PCdata
from PCfunctions import PCfuncs
from PCyaml import PCyaml
from PCmessage import PCmessage
from PCthread import PCthread
from PCweb import PCweb
from apscheduler.schedulers.background import BackgroundScheduler

# 全局数据存储
PC_data = PCdata()

# 启动时间
PC_data.update(['main','start_time'],time.time())

# 日志
PC_log = PClog()
PC_logger = PC_log.get_main_logger('主程序', level='DEBUG')
PC_data.update(['main','logger'],PC_logger)

# 日志分割线
PC_logger.debug('----------------------------------------------')
PC_logger.debug('PowerControl初始化')

# 定时器
scheduler = BackgroundScheduler()
PC_data.update(['main','scheduler'],scheduler)
scheduler.start()

# 读取环境变量
VERSION = str(os.getenv('VERSION', '版本号未知'))
WEB_PORT = int(os.getenv('WEB_PORT', '7678'))
WEB_KEY = str(os.getenv('WEB_KEY', 'admin'))
PC_logger.debug("VERSION: "+ VERSION)
PC_logger.debug("WEB_PORT: "+ str(WEB_PORT))
PC_logger.debug("WEB_KEY: "+ WEB_KEY)
PC_data.update(['main','VERSION'],VERSION)
PC_data.update(['main','WEB_PORT'],WEB_PORT)
PC_data.update(['main','WEB_KEY'],WEB_KEY)

# 存储目录路径
default_path = os.path.join(os.getcwd(), 'default')
data_path = os.path.join(os.getcwd(), 'data')
os.makedirs(data_path, exist_ok=True)
PC_data.update(['main','default_path'],default_path)
PC_data.update(['main','data_path'],data_path)

# 初始化功能模块
PC_funcs = PCfuncs()
PC_yaml = PCyaml()
PC_message = PCmessage()
PC_thread = PCthread()
PC_web = PCweb()

'''启动准备'''
# 检查目录权限
PC_funcs.check_permission(data_path,'r')
PC_funcs.check_permission(data_path,'w')
# 检查是否存在主程序和至少一个设备配置文件
PC_yaml.check_main_yaml()
PC_yaml.check_device_yaml_exist_one()
# 更新主程序配置文件
PC_yaml.update_yaml('main', 'main')
# 读取主程序配置文件
main_yaml = PC_yaml.read_yaml('main')
PC_data.update(['main','yaml'],main_yaml)
# 更新日志配置
logger_level = PC_data.get(['main','yaml','log','level'])
logger_days = int(PC_data.get(['main','yaml','log','keep_days']))
PC_log.set_all_loggers_level(logger_level)
PC_logger.debug(f'设置日志级别：{logger_level}')
PC_log.set_file_handler(backup_count=logger_days)
PC_log.start_queue_listener()
PC_log.reset_handlers(PC_logger)
PC_logger.info(f'PowerControl启动')
PC_message.send_message('Main', 'PowerControl启动')
# bemfa重连消息推送次数清零定时任务
PC_data.update(['main','bemfa_reconnect_message_count'],0)
scheduler.add_job(PC_funcs.clear_bemfa_reconnect_message_count, 'cron', hour=0, minute=0)
PC_logger.debug('bemfa重连消息推送次数重置服务已启动')
# 获取本地ip地址
local_ip = PC_funcs.get_ip_address()
PC_data.update(['main','local_ip'],local_ip)
# 兼容旧版本
PC_yaml.compatibility_check()
# 更新所有设备配置文件
PC_yaml.update_all_device_yaml()

# 启动web
PC_web_thread = threading.Thread(target=PC_web.run, daemon=True)
PC_web_thread.start()

# 启动全部设备服务
PC_thread.start_all()

# 维持主线程
PC_web_thread.join()