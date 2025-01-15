import os, threading
from PCfunctions import *
from PCweb import PCweb
from PCbemfa import PCbemfa

# 读取环境变量
web_port = int(os.getenv('WEB_PORT', '7678'))
web_key = str(os.getenv('WEB_KEY', 'admin'))
p_print("web_port: "+ str(web_port))
p_print("web_key: "+ web_key)

# 初始化配置
funcs_data = PCfuncs()
# 初始化web
pc_web = PCweb(web_port, web_key, funcs_data)
# 初始化bemfa
pc_bemfa = PCbemfa(funcs_data)

# 启动web
def run_web():
    pc_web.run()
# 接入巴法
def run_bemfa():
    pc_bemfa.run()

# 创建线程
thread_web = threading.Thread(target=run_web)
thread_bemfa = threading.Thread(target=run_bemfa)

# 启动线程
thread_web.start()
thread_bemfa.start()

# 没有定时任务加入则关闭定时
time.sleep(5)
if not funcs_data.check_job:
    funcs_data.scheduler.shutdown()

thread_web.join()
thread_bemfa.join()
