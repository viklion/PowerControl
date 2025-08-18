# PCthread.py
import threading
import time
from PCdata import PCdata
from PCservice import PCservice
from PCyaml import PCyaml

class PCthread():
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
        # 日志
        self.PC_logger = self.PC_data.get_main_logger()
        # yaml
        self.PC_yaml = PCyaml()
        # 锁
        self._lock = False
        self._lock_all = False

    """启动线程"""
    def start_thread(self, device_id):
        self.PC_logger.debug(f"设备{device_id}服务启动准备")

        # 判断设备是否存在
        if device_id not in self.PC_data.get_device_list():
            self.PC_logger.warning(f"设备{device_id}不存在，跳过启动")
            return False

        # 获取设备实例和线程
        device_object = self.get_object(device_id)
        device_thread = self.get_thread(device_id)

        # 如果设备实例不存在，则创建
        if not device_object:
            self.PC_logger.debug(f"创建{device_id}实例")
            device_object = PCservice(device_id)
            self.PC_data.update_device_service_object(device_id, device_object)
        # 如果设备线程存在且在运行，则跳过启动
        if device_thread:
            if device_thread.is_alive():
                self.PC_logger.warning(f"设备{device_id}服务已在运行，跳过启动")
                return True
            else:
                self.PC_logger.debug(f"{device_id}线程处于停止状态")

        # 生成停止信号
        stop_event = threading.Event()
        self.PC_logger.debug(f"创建{device_id}线程")
        # 创建线程
        device_thread = threading.Thread(target=device_object.start,args=(stop_event,), daemon=True)
        self.PC_data.update_device_service_thread(device_id, device_thread)

        self.PC_logger.debug(f"启动{device_id}线程")
        self.PC_logger.info(f"设备{device_id}服务正在启动")
        # 启动线程
        device_thread.start()
        return True

    """停止线程"""
    def stop_thread(self, device_id):
        self.PC_logger.debug(f"设备{device_id}服务停止准备")

        # 判断设备是否存在
        if device_id not in self.PC_data.get_device_list():
            self.PC_logger.warning(f"设备{device_id}不存在，跳过停止")
            return True

        # 获取设备实例和线程
        device_object = self.get_object(device_id)
        device_thread = self.get_thread(device_id)

        # 如果设备实例不存在，则跳过
        if not device_object or not device_thread:
            self.PC_logger.warning(f"设备{device_id}服务不存在")
            return True
        # 如果设备线程已停止，则跳过
        if not device_thread.is_alive():
            self.PC_logger.warning(f"设备{device_id}服务已经结束，跳过停止")
            return True

        self.PC_logger.info(f"设备{device_id}服务正在停止")
        # 调用停止方法
        device_object.stop()
        # 等待线程结束
        while self.is_alive(device_id):
            time.sleep(1)
        return True

    """重启线程"""
    def restart_thread(self, device_id):
        self.PC_logger.info(f"设备{device_id}服务正在重启")
        result_stop = self.stop_thread(device_id)
        result_start = self.start_thread(device_id)
        self.PC_logger.info(f"设备{device_id}服务重启完成")
        return result_stop and result_start

    # 启动全部设备服务
    def start_all(self):
        if not self._lock_all:
            self._lock_all = True
            self.PC_logger.info("全部设备服务正在启动")
            self.PC_yaml.load_all_yaml()
            device_list = self.PC_data.get_device_list()
            for device_id in device_list:
                self.start_thread(device_id)
                time.sleep(1)
            self.PC_logger.info("全部设备服务启动完毕")
            self._lock_all = False
            return True
        else:
            return False

    # 停止全部设备服务
    def stop_all(self):
        # 设置锁
        if not self._lock_all:
            self._lock_all = True
            self.PC_logger.info("全部设备服务正在停止")
            device_list = self.PC_data.get_device_list()
            for device_id in device_list:
                self.stop_thread(device_id)
            self.PC_logger.info("全部设备服务停止完毕")
            self._lock_all = False
            return True
        else:
            return False

    # 重启全部设备服务
    def restart_all(self):
        # 设置锁
        if not self._lock_all:
            self.PC_logger.info("全部设备服务正在重启")
            result_stop = self.stop_all()
            result_start = self.start_all()
            self.PC_logger.info("全部设备服务重启完毕")
            return result_stop and result_start
        else:
            return False

    """检查线程是否运行中"""
    def is_alive(self, device_id):
        device_thread = self.get_thread(device_id)
        return device_thread and device_thread.is_alive()

    """获取设备实例"""
    def get_object(self, device_id):
        object = self.PC_data.get_device_service_object(device_id)
        self.PC_logger.debug(f"获取{device_id}实例成功" if object else f"未找到{device_id}实例")
        return object

    """获取线程"""
    def get_thread(self, device_id):
        thread = self.PC_data.get_device_service_thread(device_id)
        self.PC_logger.debug(f"获取{device_id}线程成功" if thread else f"未找到{device_id}线程")
        return thread