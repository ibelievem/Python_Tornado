# @Time    : 2018/12/17 17:43
# @Author  : Niyoufa
import time


def time_consume(func):
    """函数耗时计算"""

    def wrapper(*args,**kwargs):
        start_time = time.time()
        result = func(*args,**kwargs)
        time_useage = time.time() - start_time
        print("{func_name}:{time_useage}ms".format(
            func_name=func.__name__,
            time_useage=int(time_useage*1000)
        ))
        return result
    return wrapper
