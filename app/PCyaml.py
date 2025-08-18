# PCyaml.py
import shutil
import os
import yaml
import re
from PCdata import PCdata

class PCyaml():
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
        self.PC_logger = self.PC_data.get_main_logger()

        # 默认配置路径
        self.default_path = self.PC_data.get_main_default_path()
        # 用户配置路径
        self.data_path = self.PC_data.get_main_data_path()
        # 主程序配置文件名
        self.main_yaml_filename = 'main.yaml'
        # 主程序配置文件路径
        self.main_yaml_filepath = os.path.join(self.data_path, self.main_yaml_filename)
        # 默认主程序配置文件路径
        self.default_main_yaml_filepath = os.path.join(self.default_path, self.main_yaml_filename)
        # 默认设备配置文件名
        self.default_device_yaml_filename = 'device.yaml'
        # 默认设备配置文件路径
        self.default_device_yaml_filepath = os.path.join(self.default_path, self.default_device_yaml_filename)

    # 检查main.yaml，没有则复制一份
    def check_main_yaml(self):
        if not os.path.isfile(self.main_yaml_filepath):
            try:
                # 从default目录拷贝文件到目标目录
                shutil.copy(self.default_main_yaml_filepath, self.main_yaml_filepath)
                self.PC_logger.debug(f"已生成'{self.main_yaml_filename}'")
            except Exception as e:
                self.PC_logger.error(f"生成'{self.main_yaml_filename}'失败: {e}")
        else:
            self.PC_logger.debug(f"'{self.main_yaml_filename}'存在")

    # 检查是否存在至少一个设备配置文件
    def check_device_yaml_exist_one(self):
        if not self.list_device_id():
            self.PC_logger.debug(f"未发现任何设备配置文件")
            device01_yaml_filepath = os.path.join(self.data_path, 'device01.yaml')
            try:
                # 从default目录拷贝文件到目标目录
                shutil.copy(self.default_device_yaml_filepath, device01_yaml_filepath)
                self.PC_logger.debug(f"已生成默认设备配置文件'device01.yaml'")
            except Exception as e:
                self.PC_logger.error(f"生成默认设备配置文件'device01.yaml'失败: {e}")
        else:
            self.PC_logger.debug(f"发现设备配置文件")

    # 兼容性检查
    def compatibility_check(self):
        self.PC_logger.debug("开始版本配置文件兼容性检查")
        compatibility_filepath = os.path.join(self.data_path, '.compatibility')
        if not os.path.isfile(compatibility_filepath):
            with open(compatibility_filepath, "w", encoding="utf-8") as f:
                f.write("# 新版本同步旧版本配置检查\n")
        with open(compatibility_filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f]
        if 'version_3.1_checked' not in lines:
            self.PC_logger.info("检查V3.1版本之前配置并同步至新版本")
            is_sync = self.trans_config_yaml()
            with open(compatibility_filepath, "a", encoding="utf-8") as f:
                f.write("version_3.1_checked\n")
            if is_sync:
                self.PC_logger.info("同步完成")
            else:
                self.PC_logger.info("未发现旧版本配置信息")
        self.PC_logger.debug("结束版本配置文件兼容性检查")

    # 兼容旧配置文件
    def trans_config_yaml(self):
        config_yaml_filepath = os.path.join(self.data_path, 'config.yaml')
        if os.path.isfile(config_yaml_filepath):
            self.PC_logger.info("发现旧版本'config.yaml'配置文件，开始同步")
            config_yaml_data = self.read_yaml('config')
            main_yaml_data = self.read_yaml('main')
            device01_yaml_data = self.read_yaml('device01')
            try:
                main_yaml_data['message'] = config_yaml_data['functions']['push_notifications']
                self.save_yaml('main', main_yaml_data)
                self.PC_logger.info("同步全局配置成功")
                self.reload_main_yaml()
            except Exception as e:
                self.PC_logger.error(f"从旧版本配置文件更新全局配置失败，请手动重新配置: {str(e)}")
            try:
                device01_yaml_data['bemfa'] = config_yaml_data['bemfa']
                device01_yaml_data['device'] = config_yaml_data['devices']
                device01_yaml_data['message']['enabled'] = config_yaml_data['functions']['push_notifications']['enabled']
                self.save_yaml('device01', device01_yaml_data)
                self.PC_logger.info("同步设备配置成功")
            except Exception as e:
                self.PC_logger.error(f"从旧版本配置文件更新设备配置失败，请手动重新配置: {str(e)}")
            os.rename(config_yaml_filepath, os.path.join(self.data_path, 'config_old_version.yaml'))
            return True
        else:
            return False

    # 读取默认yaml
    def read_default_yaml(self, name: str):
        '''
        :param name: yaml文件名
        '''
        yaml_filepath = os.path.join(self.default_path, f'{name}.yaml')
        try:
            with open(yaml_filepath, 'r',encoding='GBK') as f:
                self.PC_logger.debug(f"读取配置文件 '{yaml_filepath}' 成功")
                return yaml.safe_load(f)
        except Exception as e:
            self.PC_logger.error(f"读取配置文件 '{yaml_filepath}' 出错:" + str(e))
            return None

    # 读取设备yaml
    def read_yaml(self, device_id: str):
        '''
        :param device_id: yaml文件名
        '''
        yaml_filepath = os.path.join(self.data_path, f'{device_id}.yaml')
        try:
            with open(yaml_filepath, 'r',encoding='GBK') as f:
                self.PC_logger.debug(f"读取配置文件 '{device_id}.yaml' 成功")
                return yaml.safe_load(f)
        except Exception as e:
            self.PC_logger.error(f"读取配置文件 '{device_id}.yaml' 出错:" + str(e))
            return None

    # 保存设备YAML文件
    def save_yaml(self , device_id, data: dict):
        '''
        :param device_id: yaml文件名
        :param data: 数据
        '''
        yaml_filepath = os.path.join(self.data_path, f'{device_id}.yaml')
        try:
            with open(yaml_filepath, 'w',encoding='GBK') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            self.PC_logger.info(f"保存配置文件 '{device_id}.yaml' 成功")
            return True
        except Exception as e:
            self.PC_logger.error(f"保存配置文件 '{device_id}.yaml' 出错:" + str(e))
            return str(e)

    # 删除设备YAML文件
    def delete_yaml(self , device_id):
        '''
        :param device_id: yaml文件名
        '''
        yaml_filepath = os.path.join(self.data_path, f'{device_id}.yaml')
        try:
            os.remove(yaml_filepath)
            self.PC_logger.info(f"删除配置文件 '{device_id}.yaml' 成功")
            return True
        except Exception as e:
            self.PC_logger.error(f"删除配置文件 '{device_id}.yaml' 出错:" + str(e))
            return str(e)

    # 更新YAML文件
    def update_yaml(self ,device_id ,default_yaml_name):
        def compare_yaml(current_yaml_data ,default_yaml_data):
            nonlocal yaml_changed
            try:
                for key, value in default_yaml_data.items():
                    if key in current_yaml_data:
                        if isinstance(value, dict):
                            if isinstance(current_yaml_data[key], dict):
                                # 如果两个值都是字典，则递归合并
                                compare_yaml(current_yaml_data[key], value)
                            else:
                                # 如果原yaml中的值不是字典，则更新为默认值
                                current_yaml_data[key] = value
                                yaml_changed = True
                    else:
                        # 如果键在原yaml中不存在，则添加该键
                        current_yaml_data[key] = value
                        yaml_changed = True
                return True
            except Exception as e:
                yaml_changed = False
                return str(e)
        yaml_changed = False
        self.PC_logger.debug(f"检查配置文件 '{device_id}.yaml'")
        current_yaml_data = self.read_yaml(device_id)
        default_yaml_data = self.read_default_yaml(default_yaml_name)
        self.PC_logger.debug(f"对比配置文件 '{device_id}.yaml'")
        result = compare_yaml(current_yaml_data ,default_yaml_data)
        if result == True:
            if yaml_changed:
                self.save_yaml(device_id, current_yaml_data)
                self.PC_logger.debug(f"更新配置文件 '{device_id}.yaml' 成功")
            else:
                self.PC_logger.debug(f"配置文件 '{device_id}.yaml' 无需更新")
        else:
            self.PC_logger.error(f"更新配置文件 '{device_id}.yaml' 出错：{result}")

    # 获取所有设备id
    def list_device_id(self):
        self.PC_logger.debug("获取所有设备id")
        pattern = re.compile(r"^device(\d{2})\.yaml$")
        
        # 找出符合格式的文件，并去掉.yaml
        device_id_list = [
            filename[:-5]  # 去掉.yaml
            for filename in os.listdir(self.data_path)
            if os.path.isfile(os.path.join(self.data_path, filename))
            and pattern.match(filename)
        ]
        
        # 按数字部分排序
        device_id_list.sort(key=lambda device_id: int(device_id[6:]))
        return device_id_list

    # 更新所有设备配置文件
    def update_all_device_yaml(self):
        self.PC_logger.debug("开始检查配置文件更新")
        device_id_list = self.list_device_id()
        for device_id in device_id_list:
            self.update_yaml(device_id ,'device')

    # 加载所有设备配置信息
    def load_all_yaml(self):
        device_id_list = self.list_device_id()
        self.PC_logger.debug("加载所有设备配置信息")
        for device_id in device_id_list:
            self.load_yaml(device_id)

    # 加载设备配置信息
    def load_yaml(self ,device_id):
        self.PC_logger.debug(f"加载设备{device_id}配置信息")
        device_yaml_data = self.read_yaml(device_id)
        self.PC_data.update_device_yaml(device_id, device_yaml_data)

    # 重载主程序配置信息
    def reload_main_yaml(self):
        self.PC_logger.debug("重载主程序配置信息")
        main_yaml_data = self.read_yaml('main')
        self.PC_data.update_main_yaml(main_yaml_data)

    # 新建设备配置文件
    def new_yaml(self):
        self.PC_logger.debug("新建设备配置文件")
        device_id_num_list = sorted([int(item.replace('device', '')) for item in self.list_device_id()])
        id = 1
        for num in device_id_num_list:
            if num != id:
                break
            id += 1
        device_id = f'device{id:02d}'
        try:
            shutil.copy(self.default_device_yaml_filepath, os.path.join(self.data_path, f'{device_id}.yaml'))
            self.PC_logger.info(f"已生成'{device_id}.yaml'")
            return device_id
        except Exception as e:
            self.PC_logger.error(f"生成'{device_id}.yaml'失败: {e}")
            return None