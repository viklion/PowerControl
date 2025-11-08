# PCdata.py
from collections import defaultdict

def tree():
    """多层自动创建字典"""
    return defaultdict(tree)

class PCdata():
    _instance = None
    data = tree()
    '''结构
    # 包含:logger、start_time、scheduler、VERSION、WEB_PORT、WEB_KEY、default_path、data_path、yaml、local_ip、message_lock、bemfa_reconnect_message_count
    data = {
        'main': {
            'logger': logger,
            'yaml': {...},
            .......
            },   
        'device':{
            "device01":{"yaml": {...}, # 主要配置信息
                        "service": {...}, # 服务信息：object、thread、logger
                        "status": {[list]} # 设备在线状态
                        },
            device02:{"yaml": {},
                    ...}
            }
        }'''

    def __new__(cls):
        """限制只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, keys: list, default=None):
        """
        获取字典的值
        keys: list，例如 ["device01", "service", "bemfa"]
        default: 找不到时返回的默认值
        """
        d = self.data
        for key in keys:
            if key in d:
                d = d[key]
            else:
                return default
        return d
    
    def update(self, keys: list, value):
        """
        更新（或新建）多层字典的值
        keys: list，例如 ["device01", "service", "bemfa"]
        value: 任意值
        """
        d = self.data
        for key in keys[:-1]:
            d = d[key]
        d[keys[-1]] = value

    def delete(self, keys: list):
        """
        删除多层字典的某个 key
        keys: list，例如 ["device01", "service", "bemfa"]
        """
        d = self.data
        for key in keys[:-1]:
            if key in d:
                d = d[key]
            else:
                return False  # 中间层不存在
        return d.pop(keys[-1], None) is not None

    '''获取各项值'''
    def get_main_logger(self):
        return self.get(['main','logger'])

    def get_main_start_time(self):
        return self.get(['main','start_time'])

    def get_main_scheduler(self):
        return self.get(['main','scheduler'])

    def get_main_VERSION(self):
        return self.get(['main','VERSION'])

    def get_main_WEB_PORT(self):
        return self.get(['main','WEB_PORT'])

    def get_main_WEB_KEY(self):
        return self.get(['main','WEB_KEY'])

    def get_main_default_path(self):
        return self.get(['main','default_path'])

    def get_main_data_path(self):
        return self.get(['main','data_path'])

    def get_main_yaml_log_level(self):
        return self.get(['main','yaml', 'log', 'level'])

    def get_main_yaml_log_days(self):
        return self.get(['main','yaml', 'log', 'keep_days'])
    
    def get_main_yaml_message_enabled(self):
        return self.get(['main','yaml', 'message', 'enabled'])

    def get_main_yaml_message_bemfa_reconnect(self):
        return self.get(['main','yaml', 'message', 'bemfa_reconnect'])
    
    def get_main_yaml_message_ServerChan_turbo_enabled(self):
        return self.get(['main','yaml', 'message', 'ServerChan_turbo', 'enabled'])
    
    def get_main_yaml_message_ServerChan_turbo_SendKey(self):
        return self.get(['main','yaml', 'message', 'ServerChan_turbo', 'SendKey'])
    
    def get_main_yaml_message_ServerChan_turbo_channel(self):
        return self.get(['main','yaml', 'message', 'ServerChan_turbo', 'channel'])

    def get_main_yaml_message_ServerChan3_enabled(self):
        return self.get(['main','yaml', 'message', 'ServerChan3', 'enabled'])
    
    def get_main_yaml_message_ServerChan3_SendKey(self):
        return self.get(['main','yaml', 'message', 'ServerChan3', 'SendKey'])
    
    def get_main_yaml_message_Qmsg_enabled(self):
        return self.get(['main','yaml', 'message', 'Qmsg', 'enabled'])

    def get_main_yaml_message_Qmsg_Key(self):
        return self.get(['main','yaml', 'message', 'Qmsg', 'key'])
    
    def get_main_yaml_message_Qmsg_qq(self):
        return self.get(['main','yaml', 'message', 'Qmsg', 'qq'])
    
    def get_main_yaml_message_WeChat_webhook_enabled(self):
        return self.get(['main','yaml', 'message', 'WeChat_webhook', 'enabled'])
    
    def get_main_yaml_message_WeChat_webhook_url(self):
        return self.get(['main','yaml', 'message', 'WeChat_webhook', 'url'])

    def get_main_yaml_message_Gotify_enabled(self):
        return self.get(['main','yaml', 'message', 'Gotify', 'enabled'])

    def get_main_yaml_message_Gotify_url(self):
        return self.get(['main','yaml', 'message', 'Gotify', 'url'])
    
    def get_main_yaml_message_Gotify_token(self):
        return self.get(['main','yaml', 'message', 'Gotify', 'token'])

    def get_main_yaml_message_PushPlus_enabled(self):
        return self.get(['main','yaml', 'message', 'PushPlus', 'enabled'])

    def get_main_yaml_message_PushPlus_token(self):
        return self.get(['main','yaml', 'message', 'PushPlus', 'token'])
    
    def get_main_yaml_message_PushPlus_channel(self):
        return self.get(['main','yaml', 'message', 'PushPlus', 'channel'])

    def get_main_yaml_message_Bark_enabled(self):
        return self.get(['main','yaml', 'message', 'Bark', 'enabled'])

    def get_main_yaml_message_Bark_url(self):
        return self.get(['main','yaml', 'message', 'Bark', 'url'])
    
    def get_main_yaml_message_Bark_key(self):
        return self.get(['main','yaml', 'message', 'Bark', 'key'])

    def get_main_yaml_message_WeChat_app_enabled(self):
        return self.get(['main','yaml', 'message', 'WeChat_app', 'enabled'])

    def get_main_yaml_message_WeChat_app_corpid(self):
        return self.get(['main','yaml', 'message', 'WeChat_app', 'corpid'])
    
    def get_main_yaml_message_WeChat_app_agentid(self):
        return self.get(['main','yaml', 'message', 'WeChat_app', 'agentid'])

    def get_main_yaml_message_WeChat_app_secret(self):
        return self.get(['main','yaml', 'message', 'WeChat_app', 'secret'])

    def get_main_local_ip(self):
        return self.get(['main','local_ip'])

    def get_main_message_lock(self):
        return self.get(['main','message_lock'])

    def get_main_bemfa_reconnect_message_count(self):
        return self.get(['main','bemfa_reconnect_message_count'])

    def get_device_main_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'main', 'enabled'])

    def get_device_main_alias(self, device_id):
        return self.get(['device', device_id, 'yaml', 'main', 'alias'])
    
    def get_device_bemfa_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'bemfa', 'enabled'])
    
    def get_device_bemfa_uid(self, device_id):
        return self.get(['device', device_id, 'yaml', 'bemfa', 'uid'])
    
    def get_device_bemfa_topic(self, device_id):
        return self.get(['device', device_id, 'yaml', 'bemfa', 'topic'])

    def get_device_device_name(self, device_id):
        name = self.get(['device', device_id, 'yaml', 'device', 'name'])
        if name:
            return name.strip()
        else:
            return device_id
    
    def get_device_device_ip(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ip'])
    
    def get_device_device_wol_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'enabled'])

    def get_device_device_wol_method_wakeonlan(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'method', 'wakeonlan'])

    def get_device_device_wol_method_shell(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'method', 'shell'])
    
    def get_device_device_wol_mac(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'mac'])

    def get_device_device_wol_destination(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'destination'])

    def get_device_device_wol_port(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'port'])

    def get_device_device_wol_interface(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'interface'])

    def get_device_device_wol_shell_script(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'wol', 'shell_script'])
    
    def get_device_device_shutdown_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'enabled'])

    def get_device_device_shutdown_method_netrpc(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'method', 'netrpc'])

    def get_device_device_shutdown_method_udp(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'method', 'udp'])

    def get_device_device_shutdown_method_shell(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'method', 'shell'])

    def get_device_device_shutdown_account(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'account'])

    def get_device_device_shutdown_password(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'password'])

    def get_device_device_shutdown_shell_script(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'shell_script'])
    
    def get_device_device_shutdown_time(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'time'])

    def get_device_device_shutdown_timeout(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'shutdown', 'timeout'])
    
    def get_device_device_ping_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'enabled'])

    def get_device_device_ping_time(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'time'])

    def get_device_device_ping_method_pcping(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'method', 'pcping'])

    def get_device_device_ping_method_shell(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'method', 'shell'])

    def get_device_device_ping_shell_script(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'shell_script'])
    
    def get_device_device_ping_on_keyword(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'on_keyword'])

    def get_device_device_ping_off_keyword(self, device_id):
        return self.get(['device', device_id, 'yaml', 'device', 'ping', 'off_keyword'])

    def get_device_message_enabled(self, device_id):
        return self.get(['device', device_id, 'yaml', 'message', 'enabled'])

    def get_device_service_object(self, device_id):
        return self.get(['device', device_id, 'service', 'object'])

    def get_device_service_thread(self, device_id):
        return self.get(['device', device_id, 'service', 'thread'])

    def get_device_service_thread_is_alive(self, device_id):
        device_thread = self.get_device_service_thread(device_id)
        return device_thread and device_thread.is_alive()

    def get_device_service_logger(self, device_id):
        return self.get(['device', device_id, 'service', 'logger'])
    
    def get_device_status(self, device_id):
        return self.get(['device', device_id, 'status'])

    def get_device_list(self):
        return list(self.data["device"].keys())

    def get_device_alias_dict(self):
        return {
            device_id: (self.get_device_main_alias(device_id).strip().replace(" ", "-")
                        if self.get_device_main_alias(device_id) else None)
            for device_id in self.get_device_list()
        }


    '''更新数据'''
    def update_main_yaml(self, yaml: dict):
        self.update(['main','yaml'], yaml)
    
    def update_device_yaml(self, device_id, yaml: dict):
        list = ['device', device_id, 'yaml']
        self.update(list, yaml)

    def update_device_service_object(self, device_id, object):
        list = ['device', device_id, 'service', 'object']
        self.update(list, object)
    
    def update_device_service_thread(self, device_id, thread):
        list = ['device', device_id, 'service', 'thread']
        self.update(list, thread)
    
    def update_device_service_object_and_thread(self, device_id, object, thread):
        list_object = ['device', device_id, 'service', 'object']
        list_thread = ['device', device_id, 'service', 'thread']
        self.update(list_object, object)
        self.update(list_thread, thread)
    
    def update_device_service_logger(self, device_id, logger):
        list = ['device', device_id, 'service', 'logger']
        self.update(list, logger)
        
    def update_device_status(self, device_id, status: list):
        list = ['device', device_id, 'status']
        self.update(list, status)
        
    def delete_device(self, device_id):
        list = ['device', device_id]
        self.delete(list)
        return True