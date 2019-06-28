import logging
import reprlib
from tornado.options import options

# 记录日志
def logger_server_info(logger_message):
    logger = logging.getLogger("server")
    logger.info(logger_message)

# 接口日志
def api_log(*args):
    if hasattr(options, "api_debug_log") and options.api_debug_log:
        logger = logging.getLogger("api")
        print_info = ""
        for arg in args:
            print_info += "%s"%str(arg)
        logger.info(print_info)

# 程序接口日志
def repr_log(*args):
    if hasattr(options, "api_debug_log") and options.api_debug_log:
        logger = logging.getLogger("api")
        print_info = ""
        for arg in args:
            print_info += "%s"%str(arg)

        print_info = reprlib.repr(print_info)
        logger.info(print_info)