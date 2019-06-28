# @Time    : 2018/12/17 17:35
# @Author  : Niyoufa


class Rule(object):
    """
    规则父类
    """

    def condition(self, params=None, **kwargs):
        """
        判断是否符合规则
        """
        pass

    def action(self, params=None, **kwargs):
        """
        动作
        """
        pass
