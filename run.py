from PCweb import PCweb
from PowerControl import PowerControl
import os
import threading

#读取环境变量
web_port = int(os.getenv('WEB_PORT', '7678'))
web_key = str(os.getenv('WEB_KEY', 'admin'))

#初始化web
pc_web = PCweb(web_port, web_key)
#初始化bemfa
power_control = PowerControl()

#启动web
def run_web():
    pc_web.run()
#接入巴法
def run_bemfa():
    power_control.run()
        
# 创建线程
thread_a = threading.Thread(target=run_web)
thread_b = threading.Thread(target=run_bemfa)

# 启动线程
thread_a.start()
thread_b.start()

thread_a.join()
thread_b.join()
