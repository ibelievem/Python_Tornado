#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ZhangXiaocheng
# @File: calculators.py
# @Time: 2019/1/11 13:28


from collections import OrderedDict
from engine.calculator import Calculator
from calculator.personal_damage_compensation_calculator.rules import *


class NormalInjuryCompensation(Calculator):
    """普通伤害赔偿"""

    def __init__(self):
        super(NormalInjuryCompensation, self).__init__()
        self.addRule([LostIncomeRuleA(), LostIncomeRuleB(), LostIncomeRuleC()])
        self.addRule([CareCostRuleA(), CareCostRuleB(), CareCostRuleC()])
        self.addRule(HospitalMealSubsidyRule())

    def calculate(self, params, **kwargs):
        result = OrderedDict()
        for rule in self.rules:
            if isinstance(rule, list):
                for sub_rule in rule:
                    if sub_rule.condition(params, **kwargs):
                        result.update(
                            {sub_rule.name: sub_rule.action(params, **kwargs)}
                        )
            else:
                if rule.condition(params, **kwargs):
                    result.update({rule.name: rule.action(params, **kwargs)})
        return result


class DisabilityCompensation(Calculator):
    """伤残赔偿"""

    def __init__(self):
        super(DisabilityCompensation, self).__init__()
        self.addRule([DisabilityCompensationRuleA(), DisabilityCompensationRuleB(),
                      DisabilityCompensationRuleC(), DisabilityCompensationRuleD(),
                      DisabilityCompensationRuleE(), DisabilityCompensationRuleF()])
        self.addRule([SupportedAlimoneyRuleA(), SupportedAlimoneyRuleB()])
        self.addRule([LostIncomeRuleA(), LostIncomeRuleB(), LostIncomeRuleC()])
        self.addRule([CareCostRuleA(), CareCostRuleB(), CareCostRuleC()])
        self.addRule(HospitalMealSubsidyRule())

    def calculate(self, params, **kwargs):
        result = OrderedDict()
        for rule in self.rules:
            if isinstance(rule, list):
                for sub_rule in rule:
                    if sub_rule.condition(params, **kwargs):
                        result.update(
                            {sub_rule.name: sub_rule.action(params, **kwargs)}
                        )
            else:
                if rule.condition(params, **kwargs):
                    result.update({rule.name: rule.action(params, **kwargs)})
        return result


class DeathCompensation(Calculator):
    """死亡赔偿"""

    def __init__(self):
        super(DeathCompensation, self).__init__()
        self.addRule(FuneralFeeRule())
        self.addRule([SupportedAlimoneyRuleA(), SupportedAlimoneyRuleB()])
        self.addRule([DeathCompensationRuleA(), DeathCompensationRuleB(),
                      DeathCompensationRuleC(), DeathCompensationRuleD(),
                      DeathCompensationRuleE(), DeathCompensationRuleF()])
        self.addRule([LostIncomeRuleA(), LostIncomeRuleB(), LostIncomeRuleC()])
        self.addRule([CareCostRuleA(), CareCostRuleB(), CareCostRuleC()])
        self.addRule(HospitalMealSubsidyRule())

    def calculate(self, params, **kwargs):
        result = OrderedDict()
        for rule in self.rules:
            if isinstance(rule, list):
                for sub_rule in rule:
                    if sub_rule.condition(params, **kwargs):
                        result.update(
                            {sub_rule.name: sub_rule.action(params, **kwargs)}
                        )
            else:
                if rule.condition(params, **kwargs):
                    result.update({rule.name: rule.action(params, **kwargs)})
        return result
