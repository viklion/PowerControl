# PCweb.py
import os, json
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, Response, send_from_directory, jsonify
from flask_cors import CORS
from PCdata import PCdata
from PClog import PClog
from PCfunctions import PCfuncs
from PCyaml import PCyaml
from PCmessage import PCmessage
from PCthread import PCthread
from collections import defaultdict

# flask
app = Flask(__name__)
CORS(app)
app.secret_key = 'PowerControlWeb'

class PCweb():
    def __init__(self):
        global PC_data, PC_log, PC_funcs, PC_yaml, PC_message, PC_thread, PC_logger, WEB_KEY

        # 功能模块
        PC_data = PCdata()
        PC_log = PClog()
        PC_funcs = PCfuncs()
        PC_yaml = PCyaml()
        PC_message = PCmessage()
        PC_thread = PCthread()
        PC_logger = PC_data.get_main_logger()
        
        # 参数
        self.WEB_PORT = int(PC_data.get_main_WEB_PORT())
        WEB_KEY = PC_data.get_main_WEB_KEY()
        PC_logger.debug("web初始化成功")
    def run(self):
        PC_logger.info("web服务启动")
        app.run(host='0.0.0.0', port=self.WEB_PORT)

'''路由'''
# 首页跳转
@app.route('/', methods=['GET', 'POST'])
def index():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if request.method == 'POST':
        web_key = PC_funcs.trans_str(request.get_json().get('key'))
        if web_key != WEB_KEY:
            PC_logger.warning(f'ip：{user_ip} 跳转配置页失败，错误的KEY：{web_key}')
            return jsonify({"success": False, "message": "KEY不正确"}), 400
        return jsonify({"success": True})
    PC_logger.debug(f'ip：{user_ip} 访问首页')
    return render_template('index.html', VERSION=PC_funcs.get_version(), run_time= PC_funcs.run_time())

# pdf教程
@app.route('/pdf', methods=['GET'])
def pdf():
    return send_file('static/PowerControl教程.pdf', mimetype='application/pdf')

# 配置总览页
@app.route('/config', methods=['GET'])
def config():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问配置总览页失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    PC_logger.debug(f'ip：{user_ip} 访问配置总览页')
    return render_template('overview.html', VERSION=PC_funcs.get_version(), run_time= PC_funcs.run_time())

# 全局配置页
@app.route('/config/main', methods=['GET','POST'])
def config_main():
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问全局配置页失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    device_id = 'main'
    device_yaml = PC_yaml.read_yaml(device_id)
    if not device_yaml:
        return '主程序配置不存在，请重启容器尝试恢复', 404
    run_time = PC_funcs.run_time()
    if request.method == 'POST':
        device_yaml['log']['level'] = PC_funcs.trans_str(request.form.get('log.level'))
        device_yaml['log']['keep_days'] = int(request.form.get('log.keep_days'))
        device_yaml['message']['enabled'] = bool(request.form.get('message.enabled'))
        device_yaml['message']['bemfa_reconnect'] = bool(request.form.get('message.bemfa_reconnect'))
        device_yaml['message']['ServerChan_turbo']['enabled'] = bool(request.form.get('message.ServerChan_turbo.enabled'))
        device_yaml['message']['ServerChan_turbo']['SendKey'] = PC_funcs.trans_str(request.form.get('message.ServerChan_turbo.SendKey'))
        device_yaml['message']['ServerChan_turbo']['channel'] = PC_funcs.trans_str(request.form.get('message.ServerChan_turbo.channel'))
        device_yaml['message']['ServerChan3']['enabled'] = bool(request.form.get('message.ServerChan3.enabled'))
        device_yaml['message']['ServerChan3']['SendKey'] = PC_funcs.trans_str(request.form.get('message.ServerChan3.SendKey'))
        device_yaml['message']['Qmsg']['enabled'] = bool(request.form.get('message.Qmsg.enabled'))
        device_yaml['message']['Qmsg']['key'] = PC_funcs.trans_str(request.form.get('message.Qmsg.key'))
        device_yaml['message']['Qmsg']['qq'] = PC_funcs.trans_str(request.form.get('message.Qmsg.qq'))
        device_yaml['message']['WeChat_webhook']['enabled'] = bool(request.form.get('message.WeChat_webhook.enabled'))
        device_yaml['message']['WeChat_webhook']['url'] = PC_funcs.trans_str(request.form.get('message.WeChat_webhook.url'))

        # 保存配置
        save_yaml = PC_yaml.save_yaml('main', device_yaml)
        if save_yaml == True:
            PC_yaml.reload_main_yaml()
            PC_logger.info(f'设置全局日志级别：{PC_data.get_main_yaml_log_level()}')
            PC_log.set_all_loggers_level(PC_data.get_main_yaml_log_level())
            PC_logger.info(f'设置全局日志保留天数：{PC_data.get_main_yaml_log_days()}')
            flash(PC_funcs.get_time() + '\n' +'配置保存成功，已生效')
        else:
            flash(PC_funcs.get_time() + '\n' +'配置保存失败：' + str(save_yaml))
        return render_template('config-main.html', VERSION=PC_funcs.get_version(), device_id=device_id, device_name='主程序', config=device_yaml, run_time=run_time)
    PC_logger.debug(f'ip：{user_ip} 访问全局配置页')
    return render_template('config-main.html', VERSION=PC_funcs.get_version(), device_id=device_id, device_name='主程序', config=device_yaml, run_time=run_time)

# 设备配置页
@app.route('/config/<device_id>', methods=['GET','POST'])
def config_device(device_id):
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问设备配置页失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    device_yaml = PC_yaml.read_yaml(device_id)
    if not device_yaml:
        return '设备不存在', 404
    if request.method == 'POST':
        # 获取表单数据
        device_yaml['main']['enabled'] = bool(request.form.get('main.enabled'))
        device_yaml['main']['alias'] = PC_funcs.trans_str(request.form.get('main.alias')) or ''
        device_yaml['bemfa']['enabled'] = bool(request.form.get('bemfa.enabled'))
        device_yaml['bemfa']['uid'] = PC_funcs.trans_str(request.form.get('bemfa.uid'))
        device_yaml['bemfa']['topic'] = PC_funcs.trans_str(request.form.get('bemfa.topic'))
        device_yaml['device']['name'] = PC_funcs.trans_str(request.form.get('device.name'))
        device_yaml['device']['ip'] = PC_funcs.trans_str(request.form.get('device.ip'))
        device_yaml['device']['wol']['enabled'] = bool(request.form.get('device.wol.enabled'))
        device_yaml['device']['wol']['method']['wakeonlan'] = request.form.get('device.wol.method') == 'wakeonlan'
        device_yaml['device']['wol']['method']['shell'] = request.form.get('device.wol.method') == 'shell'
        device_yaml['device']['wol']['mac'] = PC_funcs.trans_str(request.form.get('device.wol.mac'))
        device_yaml['device']['wol']['destination'] = PC_funcs.trans_str(request.form.get('device.wol.destination'))
        device_yaml['device']['wol']['port'] = int(request.form.get('device.wol.port'))
        device_yaml['device']['wol']['shell_script'] = PC_funcs.trans_str(request.form.get('device.wol.shell_script'))
        device_yaml['device']['shutdown']['enabled'] = bool(request.form.get('device.shutdown.enabled'))
        device_yaml['device']['shutdown']['method']['netrpc'] = request.form.get('device.shutdown.method') == 'netrpc'
        device_yaml['device']['shutdown']['method']['udp'] = request.form.get('device.shutdown.method') == 'udp'
        device_yaml['device']['shutdown']['method']['shell'] = request.form.get('device.shutdown.method') == 'shell'
        device_yaml['device']['shutdown']['account'] = PC_funcs.trans_str(request.form.get('device.shutdown.account'))
        device_yaml['device']['shutdown']['password'] = PC_funcs.trans_str(request.form.get('device.shutdown.password'))
        device_yaml['device']['shutdown']['shell_script'] = PC_funcs.trans_str(request.form.get('device.shutdown.shell_script'))
        device_yaml['device']['shutdown']['time'] = int(request.form.get('device.shutdown.time'))
        device_yaml['device']['shutdown']['timeout'] = int(request.form.get('device.shutdown.timeout'))
        device_yaml['device']['ping']['enabled'] = bool(request.form.get('device.ping.enabled'))
        device_yaml['device']['ping']['time'] = int(request.form.get('device.ping.time'))
        device_yaml['device']['ping']['method']['pcping'] = request.form.get('device.ping.method') == 'pcping'
        device_yaml['device']['ping']['method']['shell'] = request.form.get('device.ping.method') == 'shell'
        device_yaml['device']['ping']['shell_script'] = PC_funcs.trans_str(request.form.get('device.ping.shell_script'))
        device_yaml['device']['ping']['on_keyword'] = PC_funcs.trans_str(request.form.get('device.ping.on_keyword'))
        device_yaml['device']['ping']['off_keyword'] = PC_funcs.trans_str(request.form.get('device.ping.off_keyword'))
        device_yaml['message']['enabled'] = bool(request.form.get('message.enabled'))
        # 保存配置
        save_yaml = PC_yaml.save_yaml(device_id, device_yaml)
        if save_yaml == True:
            PC_yaml.load_yaml(device_id)
            flash(PC_funcs.get_time() + '\n' +'配置保存成功，请点击重启服务生效')
        else:
            flash(PC_funcs.get_time() + '\n' +'配置保存失败：' + str(save_yaml))
        return redirect(url_for('config_device', device_id=device_id, key=web_key))

    device_status = PC_data.get_device_status(device_id)
    device_running = PC_thread.is_alive(device_id)
    device_name = f'[{PC_data.get_device_device_name(device_id)}]'
    run_time = PC_data.get_device_service_object(device_id).get_run_time() if device_running else '服务未启动'
    if device_status:
        flash(PC_funcs.get_time() + '\n' + '设备状态：' + device_status[0])
    else:
        flash(PC_funcs.get_time() + '\n' + '设备状态：未知')
    PC_logger.debug(f'ip：{user_ip} 访问设备配置页')
    return render_template('config-device.html', VERSION=PC_funcs.get_version(), device_id=device_id, device_name=device_name, config=device_yaml, run_time=run_time)

# 关机
@app.route('/shutdown/<device>', methods=['GET'])
def shutdown(device):
    # 获取请求中的密钥
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    device_id = device
    alias_dict = PC_data.get_device_alias_dict()
    for dev_id, alias in alias_dict.items():
        if alias == device.replace(' ', '-'):
            device_id = dev_id
            break
    logger = PC_data.get_device_service_logger(device_id) or PC_logger

    if web_key != WEB_KEY:
        logger.warning(f'ip：{user_ip} 访问关机api失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    logger.debug(f'ip：{user_ip} 访问关机api')

    rs = PC_funcs.pcshutdown(device_id)
    if rs:
        if 'succeeded' in rs:
            message = 'success'
            message_cn = '已发送关机指令'
            logger.info(f'{message_cn}(api) → {rs}')
        else:
            message = 'error'
            message_cn = '发送关机指令失败'
            logger.error(f'{message_cn}(api) → {rs}')
    else:
        device_name = PC_data.get_device_device_name(device_id)
        message = 'error'
        message_cn = f'设备[{device_name}]服务未启用或未运行，或远程关机未启用'
        logger.error(f'{message_cn}(api)')
    rs_json = {"device_name": PC_data.get_device_device_name(device_id),
                "device_ip": PC_data.get_device_device_ip(device_id),
                "method": "shutdown",
                "message_cn": message_cn,
                "message": message,
                "result": rs
                }
    PC_message.send_message(device_id, message_cn)
    return Response(
                json.dumps(rs_json, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200

# 网络唤醒
@app.route('/wol/<device>', methods=['GET'])
def wol(device):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    device_id = device
    alias_dict = PC_data.get_device_alias_dict()
    for dev_id, alias in alias_dict.items():
        if alias == device.replace(' ', '-'):
            device_id = dev_id
            break
    logger = PC_data.get_device_service_logger(device_id) or PC_logger

    if web_key != WEB_KEY:
        logger.warning(f'ip：{user_ip} 访问网络唤醒api失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    logger.debug(f'ip：{user_ip} 访问网络唤醒api')

    rs = PC_funcs.pcwol(device_id)
    if rs:
        if 'done' in rs:
            message = 'success'
            message_cn = '已发送唤醒指令'
            logger.info(f'{message_cn}(api)')
        else:
            message = 'error'
            message_cn = '发送唤醒指令失败'
            logger.error(f'{message_cn}(api) → {rs}')
    else:
        device_name = PC_data.get_device_device_name(device_id)
        message = 'error'
        message_cn = f'设备[{device_name}]服务未启用或未运行，或网络唤醒未启用'
        logger.error(f'{message_cn}(api)')
    rs_json = {"device_name": PC_data.get_device_device_name(device_id),
                "device_ip": PC_data.get_device_device_ip(device_id),
                "method": "wol",
                "message_cn": message_cn,
                "message": message,
                "result": rs
                }
    PC_message.send_message(device_id, message_cn)
    return Response(
                json.dumps(rs_json, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200

# ping
@app.route('/ping/<device>', methods=['GET'])
def ping(device):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    device_id = device
    alias_dict = PC_data.get_device_alias_dict()
    for dev_id, alias in alias_dict.items():
        if alias == device.replace(' ', '-'):
            device_id = dev_id
            break
    logger = PC_data.get_device_service_logger(device_id) or PC_logger

    if web_key != WEB_KEY:
        logger.warning(f'ip：{user_ip} 访问ping api失败，错误的KEY：{web_key}')
        return '请在url中填入正确的key', 401
    logger.debug(f'ip：{user_ip} 访问ping api')

    try:
        ping_result = PC_funcs.pcping(device_id)
        if ping_result:
            if 'Reply' in ping_result or 'receive on' in ping_result:
                device_status_cn = "在线"
                device_status = "on"
            elif 'timed out' in ping_result or 'receive off' in ping_result:
                device_status_cn = "离线"
                device_status = "off"
            else:
                device_status_cn = "未知"
                device_status = "unknown"
        else:
            ping_result = '设备服务未启用或未运行，或ping未启用'
            device_status_cn = "未知"
            device_status = "unknown"
        rs_json = {"device_name": PC_data.get_device_device_name(device_id),
                    "device_ip": PC_data.get_device_device_ip(device_id),
                    "method": "ping",
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
    if web_key == WEB_KEY:
        PC_logger.warning('程序退出，准备重启')
        os._exit(0)

# 测试消息推送
@app.route('/message/test', methods=['GET'])
def message_test():
    web_key = request.args.get('key')
    if web_key != WEB_KEY:
        return '请在url中填入正确的key', 401
    rs = PC_message.send_message_main('main','PowerControl消息推送测试')
    rs = {key: value for key, value in rs.items() if value is not None}
    if not rs:
        rs['warning'] = '至少启用一个消息推送渠道'
    return Response(
                json.dumps(rs, ensure_ascii=False),
                mimetype='application/json; charset=utf-8'
            ), 200

# 更新日志
@app.route('/changelog', methods=['GET'])
def change_log():
    try:
        # 读取 change.log 文件内容
        with open('change.log', 'r', encoding='GBK') as file:
            log_content = file.read()
    except Exception as e:
        log_content = "读取change.log文件失败" + ' → ' + str(e)
        PC_logger.error(log_content)
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
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问日志失败，KEY不正确（传入的KEY:{web_key}）')
        return '请在url中填入正确的key', 401
    PC_logger.debug(f'ip：{user_ip} 访问日志')
    log_dir = os.path.join('data', 'logs')
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
@app.route('/logs/get/<filename>', methods=['GET'])
def view_log_content(filename):
    web_key = request.args.get('key')
    if web_key != WEB_KEY:
        return '请在url中填入正确的key', 401
    log_path = os.path.join('data', 'logs', filename)
    # 检查文件是否存在
    if not os.path.isfile(log_path):
        return "文件不存在", 404
    try:
        # 打开并读取文件内容
        with open(log_path, 'r', encoding='utf-8', errors='replace') as file:
            log_content = file.read()
        # 返回文件内容的 JSON 数据
        return Response(
            json.dumps({'log_content': log_content}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200
    except Exception as e:
        return str(e), 500

# 删除日志文件
@app.route('/logs/delete/<filename>', methods=['DELETE'])
def delete_log(filename):
    web_key = request.args.get('key')
    if web_key != WEB_KEY:
        return '请在url中填入正确的key', 401
    
    log_path = os.path.join('data', 'logs', filename)

    # 检查文件是否存在
    if not os.path.isfile(log_path):
        return "文件不存在", 404

    try:
        if filename == 'powercontrol.log':
            PC_log.clear_log_file()
            PC_logger.info(f'已手动清空日志: {filename}')
            return '日志已清空', 200
        os.remove(log_path)
        PC_logger.info(f'已手动删除日志: {filename}')
        return '日志文件已删除', 200
    except Exception as e:
        return 'error：' + str(e), 500

# 快速生成关机指令
@app.route('/getcommand', methods=['GET', 'POST'])
def get_command():
    if request.method == 'POST':
        try:
            # 获取表单数据
            os_type = PC_funcs.trans_str(request.form['os_type'])
            power_type = PC_funcs.trans_str(request.form['power_type'])
            ip_addr = PC_funcs.trans_str(request.form['ip_addr'])
            ssh_port = int(request.form['ssh_port'])
            login_name = PC_funcs.trans_str(request.form['login_name'])
            login_passwd = PC_funcs.trans_str(request.form['login_passwd'])
            sudo_passwd = PC_funcs.trans_str(request.form['sudo_passwd'])
            delay_time = max(1, int(float(request.form['delay_time'] or 1)))

            if os_type == 'Linux':
                if power_type == 'shutdown':
                    command_main = 'poweroff'
                elif power_type == 'reboot':
                    command_main = 'reboot'
                elif power_type == 'sleep':
                    command_main = 'systemctl suspend'

                command_complete = f"""sshpass -p "{login_passwd}" ssh -o "StrictHostKeyChecking=no" -p {ssh_port} {login_name}@{ip_addr} "echo '{sudo_passwd}' | sudo -S sleep {delay_time} && echo '{sudo_passwd}' | sudo -S {command_main}" """

            elif os_type == 'MacOS':
                if power_type == 'shutdown':
                    command_main = 'shutdown -h'
                elif power_type == 'reboot':
                    command_main = 'shutdown -r'
                elif power_type == 'sleep':
                    command_main = 'shutdown -s'

                command_complete = f"""sshpass -p "{login_passwd}" ssh -o "StrictHostKeyChecking=no" -p {ssh_port} {login_name}@{ip_addr} "echo '{sudo_passwd}' | sudo -S {command_main} +{delay_time}s" """

            return command_complete

        except Exception as e:
            return "出错了：" + str(e)

    return render_template('getcommand.html')

# 新建设备配置文件
@app.route('/device/new', methods=['POST'])
def device_new():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问新建设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问新建设备服务api')
    rs = PC_yaml.new_yaml()
    if rs:
        result = True
        PC_yaml.load_yaml(rs)
    else:
        result = False
    device_id = rs

    rs_json = {"result": result,
                "device_id": device_id
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 获取主程序基本信息
@app.route('/device/get/main-basic', methods=['GET'])
def get_device_main_basic():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问获取主程序基本信息api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问获取主程序基本信息api')
    rs_json = {"version": PC_funcs.get_version(),
                "run_time": PC_funcs.run_time()
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 获取所有设备简要信息
@app.route('/device/get/all-brief', methods=['GET'])
def get_device_all_brief():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问获取所有设备简要信息api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问获取所有设备简要信息api')
    
    rs_json = defaultdict(dict)
    '''
    rs_json = {
        'device01':{
            'enabled': bool,
            'name': '',
            'alias': '',
            'ip': '',
            'running': bool,
            'status': [],
        }
    }
    '''
    rs_json['main']['log_level'] = PC_data.get_main_yaml_log_level()
    rs_json['main']['log_days'] = PC_data.get_main_yaml_log_days()
    rs_json['main']['message_enabled'] = PC_data.get_main_yaml_message_enabled()
    
    device_id_list = PC_yaml.list_device_id()
    for device_id in device_id_list:
        device_yaml = PC_yaml.read_yaml(device_id)
        rs_json[device_id]['enabled'] = device_yaml['main']['enabled']
        rs_json[device_id]['name'] = device_yaml['device']['name']
        rs_json[device_id]['alias'] = device_yaml['main']['alias']
        rs_json[device_id]['ip'] = device_yaml['device']['ip']
        rs_json[device_id]['running'] = PC_thread.is_alive(device_id)
        rs_json[device_id]['status'] = PC_data.get_device_status(device_id)

    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 获取设备配置信息
@app.route('/device/get/<device_id>', methods=['GET'])
def get_device_data(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问获取设备配置api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问获取设备配置api')
    device_yaml = PC_yaml.read_yaml(device_id)
    if device_id == 'main':
        rs_json = {"device_id": device_id,
                "device_yaml": device_yaml
                }
    else:
        device_status = PC_data.get_device_status(device_id)
        device_running = PC_thread.is_alive(device_id)
        rs_json = {"device_id": device_id,
                    "device_yaml": device_yaml,
                    "device_status": device_status,
                    "device_running": device_running
                    }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 保存设备配置信息
@app.route('/device/update/<device_id>', methods=['POST'])
def update_device_data(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问更新设备配置api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问更新设备配置信息api')
    device_yaml = request.get_json().get('device_yaml')
    rs = PC_yaml.save_yaml(device_id, device_yaml)
    if rs == True:
        result = rs
        if device_id == 'main':
            PC_yaml.reload_main_yaml()
            PC_logger.info(f'设置全局日志级别：{PC_data.get_main_yaml_log_level()}')
            PC_log.set_all_loggers_level(PC_data.get_main_yaml_log_level())
            PC_logger.info(f'设置全局日志保留天数：{PC_data.get_main_yaml_log_days()}')
        else:
            PC_yaml.load_yaml(device_id)
    else:
        result = False
    rs_json = {"device_id": device_id,
                "result": result,
                "return": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 删除设备配置信息(同时停止服务等)
@app.route('/device/delete/<device_id>', methods=['DELETE'])
def delete_device_data(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问删除设备配置api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问删除设备配置信息api')
    if device_id == 'main':
        return '无法删除主程序配置文件', 403
    del_thread = PC_thread.stop_thread(device_id)
    del_data = PC_data.delete_device(device_id)
    del_yaml = PC_yaml.delete_yaml(device_id)
    rs_json = {"device_id": device_id,
                "del_thread": del_thread,
                "del_data": del_data,
                "del_yaml": del_yaml,
                "result": del_thread and del_data and del_yaml
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 启动所有设备服务
@app.route('/device/start/all', methods=['POST'])
def start_device_service_all():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问启动所有设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问启动所有设备服务api')

    rs = PC_thread.start_all()
    rs_json = {
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 启动设备服务
@app.route('/device/start/<device_id>', methods=['POST'])
def start_device_service(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问启动设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问启动设备服务api')

    rs = PC_thread.start_thread(device_id)
    rs_json = {"device_id": device_id,
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 停止所有设备服务
@app.route('/device/stop/all', methods=['POST'])
def stop_device_service_all():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问停止所有设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问停止所有设备服务api')

    rs = PC_thread.stop_all()
    rs_json = {
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 停止设备服务
@app.route('/device/stop/<device_id>', methods=['POST'])
def stop_device_service(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问停止设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问停止设备服务api')

    rs = PC_thread.stop_thread(device_id)
    rs_json = {"device_id": device_id,
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 重启所有设备服务
@app.route('/device/restart/all', methods=['POST'])
def restart_device_service_all():
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问重启所有设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问重启所有设备服务api')

    rs = PC_thread.restart_all()
    rs_json = {
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200

# 重启设备服务
@app.route('/device/restart/<device_id>', methods=['POST'])
def restart_device_service(device_id):
    web_key = request.args.get('key')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if web_key != WEB_KEY:
        PC_logger.warning(f'ip：{user_ip} 访问重启设备服务api失败，错误的KEY：{web_key}')
        return 'denied', 401
    PC_logger.debug(f'ip：{user_ip} 访问重启设备服务api')

    rs = PC_thread.restart_thread(device_id)
    rs_json = {"device_id": device_id,
                "result": rs
                }
    return Response(
            json.dumps(rs_json, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        ), 200