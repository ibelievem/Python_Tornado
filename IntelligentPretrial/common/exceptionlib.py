_author="niyoufa"

import pdb
from tornado.web import HTTPError
from requests.exceptions import ReadTimeout, ConnectionError, ConnectTimeout
from json.decoder import JSONDecodeError
from urllib3.exceptions import MaxRetryError

# 程序异常
class ProgramException(Exception):
    def __init__(self, error_info):
        self.err = (1, error_info)

# 用户输入异常
class CustomException(Exception):

    def __init__(self,error_info):
        self.err = (2, error_info)

# token异常
class TokenException(Exception):

    def __init__(self,error_info):
        self.err = (3, error_info)

# 不存在
class NotExistsException(Exception):

    def __init__(self,error_info="不存在！"):
        self.err = (4, error_info)

# 案由异常
class CauseException(Exception):
    def __init__(self, error_info):
        self.err = (100, error_info)

# 孙艺博异常
class SunyiboException(Exception):
    def __init__(self, error_info):
        self.err = (101, error_info)

# 文书已存在
class CaseHasExistsException(Exception):
    def __init__(self, error_info):
        self.err = (102, error_info)

# 消息
class Message(Exception):
    def __init__(self, error_info):
        self.err = (200, error_info)

# API参数异常
class MissingArgumentError(Exception):
    """Exception raised by `RequestHandler.get_argument`.

    This is a subclass of `HTTPError`, so if it is uncaught a 400 response
    code will be used instead of 500 (and a stack trace will not be logged).

    .. versionadded:: 3.1
    """
    def __init__(self, arg_name):
        def __init__(self, error_info):
            self.err = (2, error_info)

def hander_response_result(response_result):
    code = (response_result or {}).get("code")
    msg = (response_result or {}).get("msg") or response_result
    if code != 0:
        import traceback
        print(traceback.format_exc())
        raise CustomException(msg)

# 抛出异常测试函数
def raiseTest():
    # 抛出异常
    raise CustomException("用户输入异常")

# 主函数
if __name__ == '__main__':
    try:
        raiseTest()
    except CustomException as msg:
       print(msg.err)