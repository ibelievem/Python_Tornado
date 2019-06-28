_author="niyoufa"

import os
import string
import time
import datetime
import hashlib
import math
import logging
import calendar
import base64
import copy
import re
import jieba
import numpy
import reprlib
import urllib.parse
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

# 打印日志到控制台
def console_log(*args):
    logger = logging.getLogger()
    logger.info(args)


"""
格式：\033[显示方式;前景色;背景色m
 2  
 3 说明：
 4 前景色            背景色           颜色
 5 ---------------------------------------
 6 30                40              黑色
 7 31                41              红色
 8 32                42              绿色
 9 33                43              黃色
10 34                44              蓝色
11 35                45              紫红色
12 36                46              青蓝色
13 37                47              白色
14 显示方式           意义
15 -------------------------
16 0                终端默认设置
17 1                高亮显示
18 4                使用下划线
19 5                闪烁
20 7                反白显示
21 8                不可见
"""
def error_print(info):
    print("\033[1;31;40m" + str(info) + "\033[0m")

def warning_print(info):
    print("\033[1;33;40m" + str(info) + "\033[0m")

def green_print(info):
    print("\033[1;32;40m" + str(info) + "\033[0m")

def green_prints(*args):
    print("\033[1;32;40m" + str(args) + "\033[0m")

def format_print(obj):
    if isinstance(obj, dict):
        print("  {")
        for k, v in obj.items():
            print("    %s : %s"%(k, v))
        print("  }")
    elif isinstance(obj, list):
        print("[")
        for sub_obj in obj:
            format_print(sub_obj)
        print("]")
    else:
        print(obj)

# 打印路由
def display_url(handlers, **kwargs):
    for handler in handlers:
        if kwargs:
            api_log(handler[0], kwargs)
        else:
            api_log(handler[0])

if __name__ == '__main__':
    # code_img, capacha_code = creat_validata_code()
    # code_img.save('/tmp/checkCode1.png')
    # print(base64encrypt("niyoufa"))
    # print(base64decrypt(base64encrypt("niyoufa")))
    # print(average_group_data([0,12,2,3,4, 18, 50, 200, 100]))
    # 0: 不限时间 1:一周内 2：半个月内 3：一个月内 10：三个月内 20：半年内  30：一年内
    # print(format_time_request_params("2016-01-01", "2017-01-01", time_string_format="%Y-%m-%d"))
    # print(remove_punctuation("放,大dff\"时代？》", extend_str="》"))
    # import pdb
    # pdb.set_trace()
    # obj = {"name":numpy.int64(10)}
    # strongdumps(obj)
    # print(type(obj["name"]))
    # print(digital_conversion("辅导费"))
    # print(soft_max([]))
    # print(chinese_to_number("二百零二"))
    # print(get_ip_from_url("http://192.168.11.88:9001/RPC2"))
    print(int_msb(1223))