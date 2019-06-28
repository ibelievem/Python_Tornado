# @Time    : 2018/12/17 17:37
# @Author  : Niyoufa


class Calculator:
    """计算器父类"""

    def __init__(self):
        self.rules = []

    def addRule(self, rule):
        """
        添加规则
        """
        self.rules.append(rule)

    def calculate(self, params, **kwargs):
        """
        执行计算
        :param params: 
        :param kwargs: 
        :return: 
        
        example:
            def calculate(self, params:Params, **kwargs):
                result = OrderedDict()
                for rule in self.rules:
                    if isinstance(rule, list):
                        for sub_rule in rule:
                            if sub_rule.condition(params, **kwargs):
                                result.update({sub_rule.name: sub_rule.action(params, **kwargs)})
                    else:
                        if rule.condition(params, **kwargs):
                            result.update({rule.name:rule.action(params, **kwargs)})
                return result
        """
        raise NotImplementedError
