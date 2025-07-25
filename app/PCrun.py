import os, threading
from PCfunctions import PCfuncs, p_print
from PCweb import PCweb
from PCbemfa import PCbemfa

# 读取环境变量
web_port = int(os.getenv('WEB_PORT', '7678'))
web_key = str(os.getenv('WEB_KEY', 'admin'))
p_print("WEB_PORT: "+ str(web_port))
p_print("WEB_KEY: "+ web_key)

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

thread_web.join()
thread_bemfa.join()
