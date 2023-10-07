import os
import logging
import time

_now_time_ = None


class Log:
    def __init__(self):
        """
        初始化日志系统
        使用以下静态方法进行日志输出:
            debug
            info
            attention
            warning
            error
            critical
        """
        #   配置日志
        logging.basicConfig(level=logging.ERROR, format="")
        #   输出带颜色log可能需要执行一次os.system("")
        os.system("")

    @staticmethod
    def refresh_time():
        """
        刷新时间
        """
        global _now_time_
        _now_time_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    #   日志输出
    @staticmethod
    def debug(msg):
        Log.refresh_time()
        logging.debug("\033[32m" + f"[{_now_time_}] DEBUG\n  {msg}\n" + "\033[0m")

    @staticmethod
    def info(msg):
        Log.refresh_time()
        logging.info(f"[{_now_time_}] INFO\n  {msg}\n")

    @staticmethod
    def attention(msg):
        """
        attention并没有增加一个日志级别，
        它和info同等，只是用于告诉开发者值得注意的信息而已
        """
        Log.refresh_time()
        logging.info("\033[94m" + f"[{_now_time_}] ATTENTION\n  {msg}\n" + "\033[0m")

    @staticmethod
    def warning(msg):
        Log.refresh_time()
        logging.warning("\033[93m" + f"[{_now_time_}] WARNING\n  {msg}\n" + "\033[0m")

    @staticmethod
    def error(msg):
        Log.refresh_time()
        logging.error("\033[91m" + f"[{_now_time_}] ERROR\n  {msg}\n" + "\033[0m")

    @staticmethod
    def critical(msg):
        Log.refresh_time()
        logging.critical("\033[91m" + f"[{_now_time_}] CRITICAL\n  {msg}\n" + "\033[0m")
