import os, json
from PCfunctions import trans_str, get_time, pcwol, pcshutdown, pcping, send_message, send_message_main, write_log, extra_log
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, Response, send_from_directory, jsonify
from flask_cors import CORS

# Flask
app = Flask(__name__)
CORS(app)
app.secret_key = 'PowerControlWeb'

# 首页跳转
@app.route('/', methods=['GET', 'POST'])
def index():
    data = {'version': WebData.fd.version}
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if request.method == 'POST':
        web_key = trans_str(request.get_json().get('key'))
        if web_key != WebData.web_key:
            extra_log(f'ip：{user_ip} 跳转配置页失败，错误的KEY：{web_key}', 3, '_web')
            return jsonify({"success": False, "message": "KEY不正确"}), 400
        return jsonify({"success": True})
    write_log(f'ip：{user_ip} 访问首页', 1, '_web')
    return render_template('index.html', config=data, run_time= WebData.fd.run_time())

# pdf教程
@app.route('/pdf', methods=['GET'])
def pdf():
    return send_file('static/PowerControl教程.pdf', mimetype='application/pdf')

# 配置页
@app.route('/config', methods=['GET', 'POST'])
def config():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WebData.web_key:
        extra_log(f'ip：{user_ip} 访问配置页失败，错误的KEY：{web_key}', 3, '_web')
        return '请在url中填入正确的key', 401
    yaml_config = WebData.fd.read_config_yaml()
    yaml_config['version'] = WebData.fd.version
    if request.method == 'POST':
        # 获取表单数据
        yaml_config['bemfa']['enabled'] = bool(request.form.get('bemfa.enabled'))
        yaml_config['bemfa']['uid'] = trans_str(request.form.get('bemfa.uid'))
        yaml_config['bemfa']['topic'] = trans_str(request.form.get('bemfa.topic'))
        yaml_config['devices']['name'] = trans_str(request.form.get('devices.name'))
        yaml_config['devices']['ip'] = trans_str(request.form.get('devices.ip'))
        yaml_config['devices']['wol']['enabled'] = bool(request.form.get('devices.wol.enabled'))
        yaml_config['devices']['wol']['mac'] = trans_str(request.form.get('devices.wol.mac'))
        yaml_config['devices']['wol']['destination'] = trans_str(request.form.get('devices.wol.destination'))
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
        yaml_config['functions']['push_notifications']['bemfa_reconnect'] = bool(request.form.get('functions.push_notifications.bemfa_reconnect'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan_turbo.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.SendKey'))
        yaml_config['functions']['push_notifications']['ServerChan_turbo']['channel'] = trans_str(request.form.get('functions.push_notifications.ServerChan_turbo.channel'))
        yaml_config['functions']['push_notifications']['ServerChan3']['enabled'] = bool(request.form.get('functions.push_notifications.ServerChan3.enabled'))
        yaml_config['functions']['push_notifications']['ServerChan3']['SendKey'] = trans_str(request.form.get('functions.push_notifications.ServerChan3.SendKey'))
        yaml_config['functions']['push_notifications']['Qmsg']['enabled'] = bool(request.form.get('functions.push_notifications.Qmsg.enabled'))
        yaml_config['functions']['push_notifications']['Qmsg']['key'] = trans_str(request.form.get('functions.push_notifications.Qmsg.key'))
        yaml_config['functions']['push_notifications']['Qmsg']['qq'] = trans_str(request.form.get('functions.push_notifications.Qmsg.qq'))
        yaml_config['functions']['push_notifications']['WeChat_webhook']['enabled'] = bool(request.form.get('functions.push_notifications.WeChat_webhook.enabled'))
        yaml_config['functions']['push_notifications']['WeChat_webhook']['url'] = trans_str(request.form.get('functions.push_notifications.WeChat_webhook.url'))
        # 保存配置
        save_yaml = WebData.fd.write_config_yaml(yaml_config)
        if save_yaml == True:
            flash(get_time() + '\n' +'配置保存成功，请重启服务或容器生效')
            extra_log('配置保存成功', 2, '_web')
        else:
            flash(get_time() + '\n' +'配置保存失败：' + str(save_yaml))
            extra_log('配置保存失败：' + str(save_yaml), 3, '_web')
        return redirect(url_for('config')+ f'?key={web_key}')
    if not WebData.fd.ping_enabled:
        flash(get_time() + '\n' +'未启用ping，设备状态未知')
    else:
        if WebData.fd.pc_state:
            flash(get_time() + '\n' + WebData.fd.device_name + ' ' + WebData.fd.pc_state[0])
        else:
            flash(get_time() + '\n' + WebData.fd.device_name + ' ' + '设备状态未知，等待下次ping查询')
    write_log(f'ip：{user_ip} 访问配置页', 1, '_web')
    return render_template('config.html', config=yaml_config, run_time= WebData.fd.run_time())

# 关机
@app.route('/shutdown', methods=['GET'])
def shutdown():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WebData.web_key:
        extra_log(f'ip：{user_ip} 访问关机接口失败，错误的KEY：{web_key}', 3, '_web')
        return '请在url中填入正确的key', 401
    write_log(f'ip：{user_ip} 访问关机接口', 1, '_web')
    rs = pcshutdown()
    if rs:
        if 'succeeded' in rs:
            message = 'success'
            message_cn = '已发送关机指令'
            extra_log(f'{message_cn}(web) || {rs}',2, '_web')
        else:
            message = 'error'
            message_cn = '发送关机指令失败'
            extra_log(f'{message_cn}(web) || {rs}' ,3, '_web')
    else:
        message = 'error'
        message_cn = '未启用远程关机'
        extra_log(f'{message_cn}(web)' ,3, '_web')
    rs_json = {"device_name": WebData.fd.device_name,
                "device_ip": WebData.fd.device_ip,
                "message_cn": message_cn,
                "message": message,
                "result": rs
                }
    send_message(message_cn)
    return Response(
                json.dumps(rs_json, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200

# 网络唤醒
@app.route('/wol', methods=['GET'])
def wol():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WebData.web_key:
        extra_log(f'ip：{user_ip} 访问网络唤醒接口失败，错误的KEY：{web_key}', 3, '_web')
        return '请在url中填入正确的key', 401
    write_log(f'ip：{user_ip} 访问网络唤醒接口', 1, '_web')
    rs = pcwol()
    if rs:
        if rs == 'done':
            message = 'success'
            message_cn = '已发送唤醒指令'
            extra_log(f'{message_cn}(web)', 2, '_web')
        else:
            message = 'error'
            message_cn = '发送唤醒指令失败'
            extra_log(f'{message_cn}(web) || {rs}' , 3, '_web')
    else:
        message = 'error'
        message_cn = '未启用网络唤醒'
        extra_log(f'{message_cn}(web)' ,3, '_web')
    rs_json = {"device_name": WebData.fd.device_name,
                "device_ip": WebData.fd.device_ip,
                "message_cn": message_cn,
                "message": message,
                "result": rs
                }
    send_message(message_cn)
    return Response(
                json.dumps(rs_json, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200

# ping
@app.route('/ping', methods=['GET'])
def ping():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WebData.web_key:
        extra_log(f'ip：{user_ip} 访问ping接口失败，错误的KEY：{web_key}', 3, '_web')
        return '请在url中填入正确的key', 401
    write_log(f'ip：{user_ip} 访问ping接口', 1, '_web')
    if not WebData.fd.ping_enabled:
        return '未启用ping!', 403
    try:
        ping_result = pcping()
        if 'Reply' in ping_result:
            device_status_cn = "在线"
            device_status = "on"
        elif 'timed out' in ping_result:
            device_status_cn = "离线",
            device_status = "off",
        rs_json = {"device_name": WebData.fd.device_name,
                    "device_ip": WebData.fd.device_ip,
                    "device_status_cn": device_status_cn,
                    "device_status": device_status,
                    "ping_result" : ping_result
                    }
        return Response(
                json.dumps(rs_json, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200
    except Exception as e:
        return 'error:' + str(e) ,200

# restart
@app.route('/restart', methods=['POST'])
def restart():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    if web_key == WebData.web_key:
        extra_log('程序退出，准备重启', 2, '_web')
        os._exit(0)

# 测试消息推送
@app.route('/testpush', methods=['GET'])
def testpush():
    web_key = request.args.get('key')
    if web_key != WebData.web_key:
        return '请在url中填入正确的key', 401
    rs = send_message_main('PowerControl消息推送测试')
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
        extra_log(log_content , 3, '_web')
    return render_template('changelog.html', log_content=log_content)

# 下载
@app.route('/download', methods=['GET'])
def download():
    file = request.args.get('file')
    if file == 'pcshutdown':
        return send_from_directory('static', 'PCshutdown.exe', as_attachment=True)
    elif file == 'wolmonitor':
        return send_from_directory('static', 'WakeOnLanMonitor.exe', as_attachment=True)

# 代码
@app.route('/code', methods=['GET'])
def copy_code():
    return render_template('code.html')

# 获取log文件列表
@app.route('/logs', methods=['GET'])
def list_logs():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WebData.web_key:
        extra_log(f'ip：{user_ip} 访问日志失败，KEY不正确（传入的KEY:{web_key}）', 3, '_web')
        return '请在url中填入正确的key', 401
    write_log(f'ip：{user_ip} 访问日志', 1, '_web')
    log_dir = WebData.fd.log_path
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
    web_key = request.args.get('key')
    if web_key != WebData.web_key:
        return '请在url中填入正确的key', 401
    log_dir = WebData.fd.log_path
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
class WebData():
    web_key = ''
    fd = ''
class PCweb():
    def __init__(self, web_port, web_key, funcs_data):
        self.web_port = web_port
        WebData.web_key = web_key
        WebData.fd = funcs_data
        extra_log("web初始化成功",2, '_web')
    def run(self):
        extra_log("web服务启动", 2, '_web')
        app.run(host='0.0.0.0', port=self.web_port)