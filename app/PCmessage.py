# PCmessage.py
import threading
import time
import requests
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
                self.PC_logger.debug(f'收到来自{device_id}的消息准备推送')
                if not type:
                    # 线程推送消息
                    send = threading.Thread(target=self.send_message_main, args=(device_id, title, desp,))
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
    def send_message_main(self, device_id, title, desp=''):
        response = {}
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_enabled()):
            # 各推送方式
            response['serverchan_turbo'] = self.send_message_serverchan_turbo(device_id, title, desp)
            response['serverchan3'] = self.send_message_serverchan3(device_id, title, desp)
            response['qmsg'] = self.send_message_qmsg(device_id, title, desp)
            response['wechat_webhook'] = self.send_message_wechat_webhook(device_id, title, desp)
            response['gotify'] = self.send_message_gotify(device_id, title, desp)
            response['pushplus'] = self.send_message_pushplus(device_id, title, desp)
            response['bark'] = self.send_message_bark(device_id, title, desp)
            response['wechat_app'] = self.send_message_wechat_app(device_id, title, desp)
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
            try:
                data = {
                        'title': f'[{device_name}]' + title,
                        'desp': self.PC_funcs.get_time() + ' ' + desp,
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
            try:
                sendkey = self.PC_data.get_main_yaml_message_ServerChan3_SendKey()
                rs = sc_send(sendkey, f'[{device_name}]' + title, self.PC_funcs.get_time() + ' ' + desp, {"tags": "PowerControl"})
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
            try:
                data = {
                        'msg': f'[{device_name}]' + title + '\n' + self.PC_funcs.get_time() + ' ' + desp,
                        'qq': self.PC_funcs.trans_str(self.PC_data.get_main_yaml_message_Qmsg_qq())
                    }
                key = self.PC_data.get_main_yaml_message_Qmsg_Key()
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

    # 企业微信群机器人推送
    def send_message_wechat_webhook(self, device_id, title, desp=''):
        if self.PC_funcs.checkbool(self.PC_data.get_main_yaml_message_WeChat_webhook_enabled()):
            device_name, logger = self.check_message_from(device_id)
            try:
                headers = {"Content-Type": "application/json"}
                data = {
                        'msgtype': 'text',
                        'text': {
                            'content': f'[{device_name}]{title}\n{self.PC_funcs.get_time()} {desp}',
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
            try:
                url_base = self.PC_data.get_main_yaml_message_Gotify_url()
                token = self.PC_data.get_main_yaml_message_Gotify_token()
                url = urljoin(url_base, f"/message?token={token}")
                data = {
                    "title": (None, f'[{device_name}]' + title),
                    "message": (None, self.PC_funcs.get_time() + ' ' + desp),
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
            try:
                headers = {"Content-Type": "application/json"}
                data = {
                        'token': self.PC_data.get_main_yaml_message_PushPlus_token(),
                        'title': f'[{device_name}]' + title,
                        'content': self.PC_funcs.get_time() + ' ' + desp,
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
            try:
                url = urljoin(self.PC_data.get_main_yaml_message_Bark_url(), "push")
                key = self.PC_data.get_main_yaml_message_Bark_key()
                data = {
                    "title": f'[{device_name}]' + title,
                    "body": self.PC_funcs.get_time() + ' ' + desp,
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
                            "content": f"[{device_name}]{title}\n{self.PC_funcs.get_time()} {desp}",
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