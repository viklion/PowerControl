from pfunctions import read_config_yaml, write_config_yaml, pcshutdown ,pcwol ,pcping ,print_and_log ,checkbool, trans_str ,get_time,write_log,send_message, return_ip
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_cors import CORS
import threading


app = Flask(__name__)
CORS(app)
app.secret_key = 'PowerControlWeb'

# 首页跳转
@app.route('/', methods=['GET', 'POST'])
def home():
    return send_file('PowerControl教程.pdf', mimetype='application/pdf')

# 配置页
@app.route('/config', methods=['GET', 'POST'])
def index():
    yaml_config = read_config_yaml()
    if not bool(yaml_config):
        return '配置文件读取失败，检查权限' ,500
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    if request.method == 'POST':
        # 获取表单数据
        yaml_config['bemfa']['enabled'] = bool(request.form.get('bemfa.enabled'))
        yaml_config['bemfa']['uid'] = trans_str(request.form.get('bemfa.uid'))
        yaml_config['bemfa']['topic'] = trans_str(request.form.get('bemfa.topic'))
        yaml_config['devices']['name'] = trans_str(request.form.get('devices.name'))
        yaml_config['devices']['ip'] = trans_str(request.form.get('devices.ip'))
        yaml_config['devices']['wol']['enabled'] = bool(request.form.get('devices.wol.enabled'))
        yaml_config['devices']['wol']['mac'] = trans_str(request.form.get('devices.wol.mac'))
        yaml_config['devices']['shutdown']['enabled'] = bool(request.form.get('devices.shutdown.enabled'))
        yaml_config['devices']['shutdown']['account'] = trans_str(request.form.get('devices.shutdown.account'))
        yaml_config['devices']['shutdown']['password'] = trans_str(request.form.get('devices.shutdown.password'))
        yaml_config['devices']['shutdown']['time'] = trans_str(request.form.get('devices.shutdown.time'))
        yaml_config['devices']['ping']['enabled'] = bool(request.form.get('devices.ping.enabled'))
        yaml_config['devices']['ping']['time'] = trans_str(request.form.get('devices.ping.time'))
        yaml_config['functions']['log']['enabled'] = bool(request.form.get('functions.log.enabled'))
        yaml_config['functions']['log']['level'] = trans_str(request.form.get('functions.log.level'))
        yaml_config['functions']['push_notifications']['enabled'] = bool(request.form.get('functions.push_notifications.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan_turbo.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.SendKey'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['channel'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.channel'))
        yaml_config['functions']['push_notifications']['ServerChan3']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan3.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan3']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan3.SendKey'))
        yaml_config['functions']['push_notifications']['Qmsg']['enabled'] = bool(request.form.get('functions.push_notifications.Qmsg.enabled'))
        yaml_config['functions']['push_notifications']['Qmsg']['key'] = trans_str(request.form.get('functions.push_notifications.Qmsg.key'))
        yaml_config['functions']['push_notifications']['Qmsg']['qq'] = trans_str(request.form.get('functions.push_notifications.Qmsg.qq'))
        yaml_config['functions']['push_notifications']['Bark']['enabled'] = bool(request.form.get('functions.push_notifications.Bark.enabled'))
        yaml_config['functions']['push_notifications']['Bark']['token'] = trans_str(request.form.get('functions.push_notifications.Bark.token'))
        
        # 保存配置
        save_yaml = write_config_yaml(yaml_config)
        if save_yaml == True:
            # Web_data.yaml_data = yaml_config
            flash(get_time() + '\n' +'配置保存成功，重启容器生效')
        else:
            flash(get_time() + '\n' +'配置保存失败：' + str(save_yaml))
        return redirect(url_for('index')+ f'?key={web_key}')
    return render_template('index.html', config=yaml_config)


@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    if not checkbool(Web_data.yaml_data['devices']['shutdown']['enabled']):
        return '未启用远程关机', 403
    # 关机
    try:
        pcshutdown()
        print_and_log("[Web]已发送关机指令" , 2)
        send_message('已发送关机指令')
        return Web_data.device_name + '已发送关机指令', 200  # 返回200 OK状态码
    except Exception as e:
        print_and_log("[Web]关机error:" + str(e) , 3)
        send_message('关机指令发送失败')
        return Web_data.device_name + '发送关机指令失败，检查配置或是否已经关机', 200
        
@app.route('/wol', methods=['GET', 'POST'])
def wol():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    if not checkbool(Web_data.yaml_data['devices']['wol']['enabled']):
        return '未启用网络唤醒', 403
    # 网络唤醒
    try:
        pcwol()
        print_and_log("[Web]已发送网络唤醒指令" , 2)
        send_message('已发送唤醒指令')
        return Web_data.device_name + '已发送网络唤醒指令', 200  # 返回200 OK状态码
    except Exception as e:
        print_and_log("[Web]唤醒error:" + str(e) , 3)
        return Web_data.device_name + '网络唤醒失败', 200

# ping
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    if not checkbool(Web_data.yaml_data['devices']['ping']['enabled']):
        return '未启用ping', 403
    try:
        ping_result = pcping()
        if 'Reply' in ping_result:
            return Web_data.device_name + '设备在线 '+ ' ' + ping_result ,200
        elif 'timed out' in ping_result:
            return Web_data.device_name + '设备离线 '+ ' ' + ping_result ,200
    except Exception as e:
        return 'error:' + str(e) ,200

class Web_data():
    yaml_data={}
    web_key=''
    device_name=''
    device_status = ''
class PCweb():
    def __init__(self, web_port, web_key):
        self.web_port = web_port
        self.web_key = web_key
        self.ping_check = None
    def set_web_data(self):
        Web_data.web_key = self.web_key
    def get_web_data(self):
        return Web_data.yaml_data
    def web_ping(self, is_power_off):
        ping_result = pcping()
        write_log('\n' + ping_result + '\n' + '---------------------', 1 ,'_ping_result')
        if 'Reply' in ping_result:
            is_power_off = False
            new_state = "在线"
        elif 'timed out' in ping_result:
            if not is_power_off:
                self.web_ping(True)
                return
            new_state = "离线"
        if Web_data.device_status != new_state:
            Web_data.device_status = new_state
            print_and_log(f"状态更新：{new_state}",2)
            send_message(f"状态更新：{new_state}")
        #开启ping定时
        self.ping_check = threading.Timer(int(Web_data.yaml_data['devices']['ping']['time']), self.web_ping, args=(is_power_off,))
        self.ping_check.start()
    
    def run(self):
        self.set_web_data()
        Web_data.yaml_data = read_config_yaml()
        device_name = trans_str(Web_data.yaml_data['devices']['name'])
        if device_name:
            device_name = f'[{device_name}]'
        Web_data.device_name = device_name
        if not checkbool(Web_data.yaml_data['bemfa']['enabled']):
            if checkbool(Web_data.yaml_data['devices']['ping']['enabled']):
                print_and_log("Ping服务启动", 2)
                self.web_ping(False)
        print_and_log("Web服务启动", 2)
        app.run(host=return_ip(), port=self.web_port)
        

if __name__ == '__main__':
    pass