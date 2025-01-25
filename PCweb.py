import os, json
from PCfunctions import *
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, Response, send_from_directory
from flask_cors import CORS


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
    yaml_config = Web_data.fd.read_config_yaml()
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
        yaml_config['devices']['shutdown']['method']['netrpc'] = bool(request.form.get('devices.shutdown.method.netrpc'))
        yaml_config['devices']['shutdown']['method']['udp'] = bool(request.form.get('devices.shutdown.method.udp'))
        yaml_config['devices']['shutdown']['method']['shell'] = bool(request.form.get('devices.shutdown.method.shell'))
        yaml_config['devices']['shutdown']['account'] = trans_str(request.form.get('devices.shutdown.account'))
        yaml_config['devices']['shutdown']['password'] = trans_str(request.form.get('devices.shutdown.password'))
        yaml_config['devices']['shutdown']['shell_script'] = trans_str(request.form.get('devices.shutdown.shell_script'))
        yaml_config['devices']['shutdown']['time'] = trans_str(request.form.get('devices.shutdown.time'))
        yaml_config['devices']['ping']['enabled'] = bool(request.form.get('devices.ping.enabled'))
        yaml_config['devices']['ping']['time'] = trans_str(request.form.get('devices.ping.time'))
        yaml_config['functions']['log']['enabled'] = bool(request.form.get('functions.log.enabled'))
        yaml_config['functions']['log']['level'] = trans_str(request.form.get('functions.log.level'))
        yaml_config['functions']['log']['clear_log']['enabled'] = bool(request.form.get('functions.log.clear_log.enabled'))
        yaml_config['functions']['log']['clear_log']['keep_days'] = trans_str(request.form.get('functions.log.clear_log.keep_days'))
        yaml_config['functions']['push_notifications']['enabled'] = bool(request.form.get('functions.push_notifications.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan_turbo.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.SendKey'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['channel'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.channel'))
        yaml_config['functions']['push_notifications']['ServerChan3']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan3.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan3']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan3.SendKey'))
        yaml_config['functions']['push_notifications']['Qmsg']['enabled'] = bool(request.form.get('functions.push_notifications.Qmsg.enabled'))
        yaml_config['functions']['push_notifications']['Qmsg']['key'] = trans_str(request.form.get('functions.push_notifications.Qmsg.key'))
        yaml_config['functions']['push_notifications']['Qmsg']['qq'] = trans_str(request.form.get('functions.push_notifications.Qmsg.qq'))
        
        # 保存配置
        save_yaml = Web_data.fd.write_config_yaml(yaml_config)
        if save_yaml == True:
            flash(get_time() + '\n' +'配置保存成功，请重启服务或容器生效')
            print_and_log('配置保存成功', 2)
        else:
            flash(get_time() + '\n' +'配置保存失败：' + str(save_yaml))
            print_and_log('配置保存失败：' + str(save_yaml), 3)
        return redirect(url_for('index')+ f'?key={web_key}')
    if not Web_data.ping_enabled:
        flash(get_time() + '\n' +'未启用ping，设备状态未知')
    else:
        if Web_data.fd.pc_state:
            flash(get_time() + '\n' + Web_data.device_name + ' ' + Web_data.fd.pc_state[0])
        else:
            flash(get_time() + '\n' + Web_data.device_name + ' ' + '设备状态未知')
    return render_template('index.html', config=yaml_config, run_time= Web_data.fd.run_time())

# 关机
@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    rs = pcshutdown()
    if rs:
        if 'succeeded' in rs:
            print_and_log("[Web]已发送关机指令" + ' || ' + rs ,2)
            send_message('已发送关机指令')
            return Web_data.device_name + '已发送关机指令' + ' || ' + rs, 200  # 返回200 OK状态码
        else:
            print_and_log("[Web]关机指令发送失败：" + ' || ' + rs ,3)
            send_message('关机指令发送失败')
            return Web_data.device_name + '发送关机指令失败，检查配置或是否已经离线' + ' | ' + rs , 200
    else:
        print_and_log('[Web]未启用远程关机！' ,3)
        send_message('未启用远程关机！')
        return '未启用远程关机！', 403

# 网络唤醒
@app.route('/wol', methods=['GET', 'POST'])
def wol():
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    rs = pcwol()
    if rs:
        if rs == True:
            print_and_log("[Web]已发送唤醒指令" , 2)
            send_message('已发送唤醒指令')
            return Web_data.device_name + '已发送唤醒指令', 200  # 返回200 OK状态码
        else:
            print_and_log("[Web]发送唤醒指令失败:" + rs , 3)
            send_message('发送唤醒指令失败')
            return Web_data.device_name + '发送唤醒指令失败', 200
    else:
        print_and_log('[Web]未启用网络唤醒！' ,3)
        send_message('未启用网络唤醒！')
        return '未启用网络唤醒！', 403

# ping
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    if not Web_data.ping_enabled:
        return '未启用ping!', 403
    try:
        ping_result = pcping()
        if 'Reply' in ping_result:
            rs = {"device_name": Web_data.device_name, "device_status_cn": "在线" ,"device_status": "on" , "ping_result" : ping_result}
        elif 'timed out' in ping_result:
            rs = {"device_name": Web_data.device_name, "device_status_cn": "离线" ,"device_status": "off" , "ping_result" : ping_result}
        return Response(
                json.dumps(rs, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200
    except Exception as e:
        return 'error:' + str(e) ,200

# restart
@app.route('/restart', methods=['POST'])
def restart():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key == Web_data.web_key:
        os._exit(0)

# 测试消息推送
@app.route('/testpush', methods=['GET'])
def testpush():
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    rs = send_message('PowerControl消息推送测试')
    rs = {key: value for key, value in rs.items() if value is not None}
    if rs:
        return Response(
                json.dumps(rs, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200
    else:
        return '至少启用一个推送通道'

# 更新日志
@app.route('/changelog', methods=['GET'])
def change_log():
    try:
        # 读取 change.log 文件内容
        with open('change.log', 'r', encoding='GBK') as file:
            log_content = file.read()
    except Exception as e:
        log_content = "读取change.log文件失败" + ' || ' + str(e)
        print_and_log(log_content , 3)
    return render_template('changelog.html', log_content=log_content)

# 下载
@app.route('/download', methods=['GET'])
def download():
    return send_from_directory('static', 'PCshutdown.exe', as_attachment=True)

# 代码
@app.route('/code', methods=['GET'])
def copy_code():
    return render_template('code.html')

# 获取log文件列表
@app.route('/logs', methods=['GET'])
def list_logs():
    web_key = request.args.get('key')
    if web_key != Web_data.web_key:
        return '请在url中填入正确的key', 401
    log_dir = Web_data.fd.log_path
    # 检查目录是否存在
    if not os.path.exists(log_dir):
        return "日志目录不存在", 404
    # 获取目录中的所有 .log 文件
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    # 倒序排列
    log_files.sort(reverse=True)
    # 返回文件列表
    return render_template('logs.html', log_files=log_files)

# 查看log文件内容
@app.route('/logs/<filename>', methods=['GET'])
def view_log_content(filename):
    log_dir = Web_data.fd.log_path
    log_path = os.path.join(log_dir, filename)
    # 检查文件是否存在
    if not os.path.isfile(log_path):
        return "文件不存在", 404
    try:
        # 打开并读取文件内容
        with open(log_path, 'r', encoding='GBK') as file:
            log_content = file.read()
        # 返回文件内容的 JSON 数据
        return Response(
            json.dumps({'log_content': log_content}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200
    except Exception as e:
        return str(e), 500
'''---------------------------------------------------------------------------------'''
class Web_data():
    web_key=''
    fd = None
    device_name=''
    ping_enabled = False
class PCweb():
    def __init__(self, web_port, web_key, funcs_data):
        self.web_port = web_port
        self.web_key = web_key
        self.fd = funcs_data
        print_and_log("web初始化成功",2)
    def set_web_data(self):
        Web_data.web_key = self.web_key
        Web_data.fd =self.fd
        Web_data.ping_enabled = self.fd.ping_enabled
        Web_data.device_name = self.fd.device_name
    def run(self):
        self.set_web_data()
        print_and_log("web服务启动", 2)
        app.run(host='0.0.0.0', port=self.web_port)
