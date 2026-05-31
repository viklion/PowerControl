# PCmessage.py
import threading
import time
import requests
import json
from PCdata import PCdata
from PCfunctions import PCfuncs
from pythonping import ping
from serverchan_sdk import sc_send
from datetime import datetime, timedelta
from urllib.parse import urljoin

class PCmessage():
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
        self.PC_funcs = PCfuncs()
        self.PC_logger = self.PC_data.get_main_logger()
        self.message_wechat_app_access_token = ''
        self.message_wechat_app_expire_time = ''

    # 消息推送
    def send_message(self, device_id, title, desp='', type=''):
        # 是否启用全局消息推送
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_enabled()):
            # 是否启用设备消息推送
            if device_id == 'main' or self.PC_data.get_device_message_enabled(device_id):
                if device_id == 'main':
                    message_channel_enabled = self.PC_data.get_main_yaml_message_channel_enabled()
                    channel = None if not message_channel_enabled else self.PC_data.get_main_yaml_message_channel_channel()
                else:
                    message_channel_enabled = self.PC_data.get_device_message_channel_enabled(device_id)
                    channel = None if not message_channel_enabled else self.PC_data.get_device_message_channel_channel(device_id)
                self.PC_logger.debug(f'收到来自{device_id}的消息准备推送')
                if not type:
                    # 线程推送消息
                    send = threading.Thread(target=self.send_message_main, args=(device_id, title, desp, channel,))
                    send.start()
                # 巴法重连的消息
                elif type == 'bemfa_reconnect':
                    # 消息锁，同一时间只允许发送1次重连消息
                    if not self.PC_data.get_main_message_lock():
                        self.PC_data.update(['main', 'message_lock'], True)
                        # 计数
                        bemfa_reconnect_message_count = self.PC_data.get_main_bemfa_reconnect_message_count()
                        bemfa_reconnect_message_count += 1
                        self.PC_data.update(['main', 'bemfa_reconnect_message_count'], bemfa_reconnect_message_count)
                        # 5次后不再发送
                        if bemfa_reconnect_message_count <= 5:
                            re_send = threading.Thread(target=self.re_send_message_bemfa, args=(device_id, title, desp,))
                            re_send.start()
            else:
                self.PC_logger.debug(f'收到来自{device_id}的消息，设备消息推送未启用跳过')
        else:
            self.PC_logger.debug(f'收到来自{device_id}的消息，全局消息推送未启用跳过')
    def send_message_main(self, device_id, title, desp='', channel=None):
        response = {}
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_enabled()):
            send_funcs = {
                'serverchan_turbo': self.send_message_serverchan_turbo,
                'serverchan3': self.send_message_serverchan3,
                'qmsg': self.send_message_qmsg,
                'qmsgpvt': self.send_message_qmsgpvt,
                'wechat_webhook': self.send_message_wechat_webhook,
                'gotify': self.send_message_gotify,
                'pushplus': self.send_message_pushplus,
                'bark': self.send_message_bark,
                'wechat_app': self.send_message_wechat_app,
                'webhook': self.send_message_webhook,
            }
            if channel is None:
                for name, func in send_funcs.items():
                    response[name] = func(device_id, title, desp)
            else:
                func = send_funcs.get(channel)
                response[channel] = func(device_id, title, desp)
        return response

    # 断网下等待网络恢复重新发送
    def re_send_message_bemfa(self, device_id, title, desp):
        while True:
            try:
                rs = str(ping('www.baidu.com', timeout = 1, count = 1))
            except:
                time.sleep(10)
                continue
            if 'timed out' in rs:
                time.sleep(10)
                continue
            elif 'Reply' in rs:
                self.send_message(device_id,title, desp)
                # 解锁消息锁
                time.sleep(300)
                self.PC_data.update(['main', 'message_lock'], False)
                break

    # 判断主程序或设备消息，选择不同logger
    def check_message_from(self, device_id):
        if device_id == 'main':
            device_name = '主程序'
            logger = self.PC_logger
        else:
            device_name = self.PC_data.get_device_device_name(device_id)
            logger = self.PC_data.get_device_service_logger(device_id)
        return device_name, logger

    # Server酱Turbo推送
    def send_message_serverchan_turbo(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_ServerChan_turbo_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                data = {
                        'title': title,
                        'desp': content,
                        'channel': self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_ServerChan_turbo_channel())
                    }
                sendkey = self.PC_data.get_main_yaml_message_ServerChan_turbo_SendKey()
                rs = requests.post(f'https://sctapi.ftqq.com/{sendkey}.send', data=data).json()
                logger.debug("Server酱Turbo推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Server酱Turbo推送消息出错：" + rs)
                return rs

    # Server酱3推送
    def send_message_serverchan3(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_ServerChan3_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                sendkey = self.PC_data.get_main_yaml_message_ServerChan3_SendKey()
                rs = sc_send(sendkey, title, content, {"tags": "PowerControl"})
                logger.debug("Server酱3推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Server酱3推送消息出错：" + rs)
                return rs

    # Qmsg酱推送
    def send_message_qmsg(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_Qmsg_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                data = {
                        'msg': title + '\n' + content,
                        'qq': self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_Qmsg_qq())
                    }
                key = self.PC_data.get_main_yaml_message_Qmsg_key()
                rs = requests.post(f'https://qmsg.zendee.cn/send/{key}', data=data).json()
                # 移除 'ad' 广告字段
                if 'ad' in rs:
                    del rs['ad']
                logger.debug("Qmsg酱推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Qmsg酱推送消息出错：" + rs)
                return rs

    # Qmsg私有云推送
    def send_message_qmsgpvt(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_Qmsgpvt_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            url_base = self.PC_data.get_main_yaml_message_Qmsgpvt_url()
            send_type = self.PC_data.get_main_yaml_message_Qmsgpvt_type()
            if send_type == 'qq':
                qq = self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_Qmsgpvt_qq())
                url_splice = 'send'
            elif send_type == 'qqgroup':
                qq = self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_Qmsgpvt_qqgroup())
                url_splice = 'group'
            try:
                data = {
                        'msg': title + '\n' + content,
                        'qq': qq,
                        'bot': self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_Qmsgpvt_bot())
                    }
                key = self.PC_data.get_main_yaml_message_Qmsgpvt_key()
                url = urljoin(url_base, f"/{url_splice}/{key}")
                rs = requests.post(url, data=data).json()
                # 移除 'ad' 广告字段
                if 'ad' in rs:
                    del rs['ad']
                logger.debug("Qmsg私有云推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Qmsg私有云推送消息出错：" + rs)
                return rs

    # 企业微信群机器人推送
    def send_message_wechat_webhook(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_WeChat_webhook_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                headers = {"Content-Type": "application/json"}
                data = {
                        'msgtype': 'text',
                        'text': {
                            'content': f'{title}\n{content}',
                            },
                    }
                url = self.PC_data.get_main_yaml_message_WeChat_webhook_url()
                rs = requests.post(url, json=data, headers=headers).json()
                logger.debug("企业微信群机器人推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("企业微信群机器人推送消息出错：" + rs)
                return rs

    # Gotify推送
    def send_message_gotify(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_Gotify_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                url_base = self.PC_data.get_main_yaml_message_Gotify_url()
                token = self.PC_data.get_main_yaml_message_Gotify_token()
                url = urljoin(url_base, f"/message?token={token}")
                data = {
                    "title": (None, title),
                    "message": (None, content),
                }
                rs = requests.post(url, files=data).json()
                logger.debug("Gotify推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Gotify推送消息出错：" + rs)
                return rs

    # PushPlus推送
    def send_message_pushplus(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_PushPlus_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                headers = {"Content-Type": "application/json"}
                data = {
                        'token': self.PC_data.get_main_yaml_message_PushPlus_token(),
                        'title': title,
                        'content': content,
                        'channel': self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_PushPlus_channel())
                    }
                rs = requests.post(f'https://www.pushplus.plus/send/', json=data, headers=headers).json()
                logger.debug("PushPlus推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("PushPlus推送消息出错：" + rs)
                return rs

    # Bark推送
    def send_message_bark(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_Bark_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                url = urljoin(self.PC_data.get_main_yaml_message_Bark_url(), "push")
                key = self.PC_data.get_main_yaml_message_Bark_key()
                data = {
                    "title": title,
                    "body": content,
                    "device_key": key
                }
                rs = requests.post(url, json=data).json()
                logger.debug("Bark推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Bark推送消息出错：" + rs)
                return rs

    # 企业微信应用推送
    def send_message_wechat_app(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_WeChat_app_enabled()):
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            # 判断access_token是否过期
            if not self.message_wechat_app_access_token or datetime.now() >= self.message_wechat_app_expire_time:
                # 获取access_token
                try:
                    corpid = self.PC_data.get_main_yaml_message_WeChat_app_corpid()
                    secret = self.PC_data.get_main_yaml_message_WeChat_app_secret()
                    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}'
                    # 发送GET请求
                    rs = requests.get(url).json()
                    # 判断返回状态
                    if rs.get("errcode") == 0:
                        self.message_wechat_app_access_token = rs.get("access_token")
                        expires_in = rs.get("expires_in", 0)
                        # 计算过期时间
                        self.message_wechat_app_expire_time = datetime.now() + timedelta(seconds=expires_in)
                        logger.debug(f"企业微信应用推送获取access_token成功")
                    else:
                        logger.error(f"企业微信应用推送获取access_token失败: {rs.get('errmsg')} (errcode={rs.get('errcode')})")
                        return rs
                except Exception as e:
                    rs = str(e)
                    logger.error("企业微信应用推送获取access_token出错：" + rs)
                    return rs
            try:
                agentid = self.PC_data.get_main_yaml_message_WeChat_app_agentid()
                url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.message_wechat_app_access_token}'
                headers = {"Content-Type": "application/json"}
                data = {
                        "touser" : "@all",
                        "msgtype" : "text",
                        "agentid" : agentid,
                        "text": {
                            "content": f"{title}\n{content}",
                            },
                    }
                rs = requests.post(url, json=data, headers=headers).json()
                if not rs.get("errcode") == 0:
                    if rs.get("errcode") == 40014:
                        # access_token失效，下次重新获取
                        self.message_wechat_app_access_token = ''
                        self.message_wechat_app_expire_time = ''
                    logger.error(f"企业微信应用推送失败: {rs.get('errmsg')} (errcode={rs.get('errcode')})")
                    return rs
                logger.debug("企业微信应用推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("企业微信应用推送出错：" + rs)
                return rs

    # 自定义webhook推送
    def send_message_webhook(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_Webhook_enabled()):
            send_Method = self.PC_data.get_main_yaml_message_Webhook_Method()
            send_Url = self.PC_data.get_main_yaml_message_Webhook_Url()
            send_ContentType = self.PC_data.get_main_yaml_message_Webhook_ContentType()
            send_Headers = json.loads(self.PC_data.get_main_yaml_message_Webhook_Headers())
            send_Body = json.loads(self.PC_data.get_main_yaml_message_Webhook_Body())
            device_name, logger = self.check_message_from(device_id)
            title, content = self.message_template_handle(device_id, device_name, title, desp)
            try:
                headers = {"Content-Type": "application/json"}
                headers.update(send_Headers)
                variables = {
                    "$title": title,
                    "$content": content,
                }
                data = {}
                for k, v in send_Body.items():
                    for var, value in variables.items():
                        v = v.replace(var, str(value))
                    data[k] = v
                rs = requests.post(send_Url, json=data, headers=headers).json()
                logger.debug("Webhook推送返回:" + str(rs))
                return rs
            except Exception as e:
                rs = str(e)
                logger.error("Webhook推送消息出错：" + rs)
                return rs

    def message_template_handle(self, device_id, device_name, title, desp):
        variables = {
            "name": f'[{device_name}]',
            "title": title,
            "time": self.PC_funcs.get_time(),
            "content": desp,
        }

        def replace_variables(text):
            for key, value in variables.items():
                text = text.replace(f"${key}", str(value))
            return text

        if device_id == 'main':
            enabled = self.PC_data.get_main_yaml_message_template_enabled()
        else:
            enabled = self.PC_data.get_device_message_template_enabled(device_id)
        if enabled:
            if device_id == 'main':
                template_title = self.PC_data.get_main_yaml_message_template_title()
                template_content = self.PC_data.get_main_yaml_message_template_content()
            else:
                template_title = self.PC_data.get_device_message_template_title(device_id)
                template_content = self.PC_data.get_device_message_template_content(device_id)
            title = replace_variables(template_title)
            content = replace_variables(template_content)
        else:
            title = f'[{device_name}]' + title
            content = self.PC_funcs.get_time() + ' ' + desp
        return title, content
        