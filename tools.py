#   用于放置各种需要使用的方法

import os
import logging


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
        logging.basicConfig(level=logging.DEBUG, format="")
        #   输出带颜色log可能需要执行一次os.system("")
        os.system("")

    #   日志输出
    @staticmethod
    def debug(msg):
        logging.debug("\033[32m" + f"DEBUG\n  {msg}" + "\033[0m")

    @staticmethod
    def info(msg):
        logging.info(f"INFO\n  {msg}")

    @staticmethod
    def attention(msg):
        """
        attention并没有增加一个日志级别，
        它和info同等，只是用于告诉开发者值得注意的信息而已
        """
        logging.info("\033[94m" + f"ATTENTION\n  {msg}" + "\033[0m")

    @staticmethod
    def warning(msg):
        logging.warning("\033[93m" + f"WARNING\n  {msg}" + "\033[0m")

    @staticmethod
    def error(msg):
        logging.error("\033[91m" + f"ERROR\n  {msg}" + "\033[0m")

    @staticmethod
    def critical(msg):
        logging.critical("\033[91m" + f"CRITICAL\n  {msg}" + "\033[0m")