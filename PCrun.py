import os, threading
from PCfunctions import *
from PCweb import PCweb
from PCbemfa import PCbemfa

#读取环境变量
web_port = int(os.getenv('WEB_PORT', '7678'))
web_key = str(os.getenv('WEB_KEY', 'admin'))
p_print("web_port: "+ str(web_port))
p_print("web_key: "+ web_key)

#初始化配置
data_funcs = PCfuncs()
#初始化web
pc_web = PCweb(web_port, web_key, data_funcs)
#初始化bemfa
pc_bemfa = PCbemfa(data_funcs)

#启动ping
data_funcs.start_ping()
#启动web
def run_web():
    pc_web.run()
#接入巴法
def run_bemfa():
    pc_bemfa.run()
        
# 创建线程
thread_a = threading.Thread(target=run_web)
thread_b = threading.Thread(target=run_bemfa)

# 启动线程
thread_a.start()
thread_b.start()

thread_a.join()
thread_b.join()