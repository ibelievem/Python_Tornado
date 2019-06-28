# @Time    : 2018/12/17 20:46
# @Author  : Niyoufa


class Params(object):
    """计算参数"""

    def __init__(self, data):
        if not isinstance(data, dict):
            self.data = {}
        self.data = data
        for k, v in self.data.items():
            self.__setattr__(k, v)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return "<Context {}>".format(self.data)
