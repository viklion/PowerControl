# PClog.py
import logging
import os
import time
import queue
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
from colorlog import ColoredFormatter

# 自定义文件轮转，main.YYYY-MM-DD.log 格式
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def rotation_filename(self, default_name):
        timestamp = time.strftime("%Y-%m-%d", time.localtime(self.rolloverAt - self.interval))
        prefix, _ = os.path.splitext(self.baseFilename)
        return f"{prefix}.{timestamp}.log"

class PClog():
    _instance = None
    def __new__(cls):
        """限制只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ===== 全局日志配置 =====
    # 格式
    FMT = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
    DATEFMT = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(FMT, datefmt=DATEFMT)

    # 彩色控制台格式
    COLOR_FMT = f"%(log_color)s{FMT}"
    color_formatter = ColoredFormatter(
        COLOR_FMT,
        datefmt=DATEFMT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
    )

    # ===== Queue 相关 =====
    log_queue = queue.Queue()
    queue_listener = None

    # ===== 全局唯一 Handler =====
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    file_handler = None

    # ===== 获取 logger 函数 =====
    # 主程序logger
    def get_main_logger(self, name: str, level="INFO"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.addHandler(self.console_handler)
            logger.setLevel(self.trans_level(level))
        return logger
    # 设备服务logger
    def get_logger(self, name: str, level="INFO"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.addHandler(QueueHandler(self.log_queue))
            logger.setLevel(self.trans_level(level))
        return logger

    # 删除指定 logger
    def remove_logger(self, name: str):
        logger = logging.getLogger(name)
        # 1. 移除并关闭所有 handler
        for h in logger.handlers[:]:
            logger.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
        # 2. 从 logging 注册表中删除
        logging.Logger.manager.loggerDict.pop(name, None)
        # 3. 防止后续引用
        del logger

    # 检查重复logger
    def check_duplicate_logger(self, name: str):
        logger = logging.getLogger(name)
        if logger.handlers:
            return True

    # 设置日志文件
    def set_file_handler(self, when='midnight'):
        log_dir = os.path.join('data', 'logs')
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, 'powercontrol.log')
        self.file_handler = CustomTimedRotatingFileHandler(
            filename=log_file,
            when=when,
            interval=1,
            encoding='utf-8'
        )
        self.file_handler.setFormatter(self.formatter)
    def reset_handlers(self, logger):
        logger.removeHandler(self.console_handler)
        logger.addHandler(QueueHandler(self.log_queue))

    # 开启日志队列
    def start_queue_listener(self):
        self.queue_listener = QueueListener(self.log_queue, self.console_handler, self.file_handler)
        self.queue_listener.start()

    # 日志等级转换
    def trans_level(self, level):
        mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        return mapping.get(level.upper(), logging.INFO)

    # ===== 批量修改所有 logger 等级 =====
    def set_all_loggers_level(self, level: str):
        target_level = self.trans_level(level)
        for logger_name in logging.root.manager.loggerDict.keys():
            logging.getLogger(logger_name).setLevel(target_level)

    # 清空日志
    def clear_log_file(self):
        self.file_handler.acquire()  # 获取锁，防止多线程写入冲突
        try:
            self.file_handler.stream.truncate(0)  # 清空文件
            self.file_handlerh.stream.seek(0)       # 移动文件指针到开头
        except Exception as e:
            print(f"清空日志文件失败: {e}")
        finally:
            self.file_handler.release()