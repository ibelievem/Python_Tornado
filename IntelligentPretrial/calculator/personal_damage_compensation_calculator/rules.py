#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ZhangXiaocheng
# @File: rules.py
# @Time: 2019/1/9 14:21


from engine.rule import Rule
from .rule_models import CalculatorModel
from microserver.core.exceptions import ArgumentTypeError


# 普通伤害赔偿（通用）
# 误工费
class LostIncomeRuleA(Rule):

    name = '误工费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """受害人有固定收入"""
        if params.victim_have_fixed_income:
            return True

    def action(self, params=None, **kwargs):
        victim_income = params.victim_income  # 元
        delay = params.delay  # 天
        lost_income = victim_income * delay
        return lost_income


class LostIncomeRuleB(Rule):

    name = '误工费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """受害人无固定收入且可以举证"""
        if not params.victim_have_fixed_income and params.victim_can_prove:
            return True

    def action(self, params=None, **kwargs):
        victim_threeyear_annual_income = params.victim_threeyear_annual_income
        delay = params.delay
        lost_income = int(victim_threeyear_annual_income * delay / 365)
        return lost_income


class LostIncomeRuleC(Rule):

    name = '误工费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """受害人无固定收入且不能举证"""
        if not params.victim_have_fixed_income and not params.victim_can_prove:
            return True

    def action(self, params=None, **kwargs):
        delay = params.delay
        victim_job_annual_income = params.victim_job_annual_income
        lost_income = int(victim_job_annual_income * delay / 365)
        return lost_income


# 护理费
class CareCostRuleA(Rule):

    name = '护理费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """护理人员有固定收入"""
        if params.carer_have_fixed_income:
            return True

    def action(self, params=None, **kwargs):
        carer_income = params.carer_income
        care_days = params.care_days
        care_cost = carer_income * care_days
        return care_cost


class CareCostRuleB(Rule):

    name = '护理费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """护理人员无固定收入且可以举证"""
        if not params.carer_have_fixed_income and params.carer_can_prove:
            return True

    def action(self, params=None, **kwargs):
        carer_threeyear_annual_income = params.carer_threeyear_annual_income
        care_days = params.care_days
        care_cost = int(carer_threeyear_annual_income * care_days / 365)
        return care_cost


class CareCostRuleC(Rule):

    name = '护理费'

    def __init__(self):
        pass

    def condition(self, params=None, **kwargs):
        """护理人员无固定收入且不能举证或雇佣护工"""
        if not params.carer_have_fixed_income and not params.carer_can_prove:
            return True

    def action(self, params=None, **kwargs):
        local_carer_income = params.local_carer_income
        care_days = params.care_days
        care_cost = local_carer_income * care_days
        return care_cost


# 住院伙食补助费
class HospitalMealSubsidyRule(Rule):

    name = '住院伙食补助费'

    def __init__(self):
        self.region_standard = CalculatorModel().get_region_standard_map()

    def condition(self, params=None, **kwargs):
        return True

    def action(self, params=None, **kwargs):
        region = params.region
        hospital_stay = params.hospital_stay
        try:
            subsidy_standard = self.region_standard[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = int(hospital_stay * subsidy_standard)
        return fee


# 伤残赔偿
# 残疾赔偿金
class DisabilityCompensationRuleA(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        """城镇居民且年龄≤60周岁"""
        if params.victim_is_urban and params.victim_age <= 60:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            disposable_income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(disposable_income * 20 * coefficient)
        return compensation


class DisabilityCompensationRuleB(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        """城镇居民且年龄60-75周岁"""
        if params.victim_is_urban and 60 < params.victim_age < 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        age = params.victim_age
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            disposable_income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(disposable_income * (20 - (age - 60)) * coefficient)
        return compensation


class DisabilityCompensationRuleC(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        """城镇居民且年龄≥75周岁"""
        if params.victim_is_urban and params.victim_age >= 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            disposable_income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(disposable_income * 5 * coefficient)
        return compensation


class DisabilityCompensationRuleD(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        """农村居民且年龄≤60周岁"""
        if not params.victim_is_urban and params.victim_age <= 60:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(income * 20 * coefficient)
        return compensation


class DisabilityCompensationRuleE(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        """农村居民且年龄60-75周岁"""
        if not params.victim_is_urban and 60 < params.victim_age < 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        age = params.victim_age
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(income * (20 - (age - 60)) * coefficient)
        return compensation


class DisabilityCompensationRuleF(Rule):

    name = '残疾赔偿金'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        """农村居民且年龄≥75周岁"""
        if not params.victim_is_urban and params.victim_age >= 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        compensation = int(income * 5 * coefficient)
        return compensation


# 被扶养人生活费
# TODO(zxc): Specialize, suspensory
class SupportedAlimoneyRuleA(Rule):

    name = '被扶养人生活费'

    def __init__(self):
        self.model = CalculatorModel()
        self.region_urban_expend = self.model.get_region_urban_expend_map()
        self.region_rural_expend = self.model.get_region_rural_expend_map()

    def condition(self, params=None, **kwargs):
        # 受害人城镇户口
        if params.victim_is_urban:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        supporteds = params.supporteds
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            urban_expend = self.region_urban_expend[region]
            rural_expend = self.region_rural_expend[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fees, fees_with_age, years = self.model.supported_alimoney(coefficient,
                                                                   urban_expend,
                                                                   rural_expend,
                                                                   supporteds)
        sum_fee = sum(fees)
        if sum_fee >= urban_expend:
            max_year = max(years)
            final_fee = max_year * urban_expend
        else:
            final_fee = sum(fees_with_age)
        return final_fee


class SupportedAlimoneyRuleB(Rule):

    name = '被扶养人生活费'

    def __init__(self):
        self.model = CalculatorModel()
        self.region_urban_expend = self.model.get_region_urban_expend_map()
        self.region_rural_expend = self.model.get_region_rural_expend_map()

    def condition(self, params=None, **kwargs):
        # 受害人农村户口
        if not params.victim_is_urban:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        level = params.level
        supporteds = params.supporteds
        coefficient = round((1.1 - 0.1 * level), 1)
        try:
            urban_expend = self.region_urban_expend[region]
            rural_expend = self.region_rural_expend[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fees, fees_with_age, years = self.model.supported_alimoney(coefficient,
                                                                   urban_expend,
                                                                   rural_expend,
                                                                   supporteds)
        sum_fee = sum(fees)
        if sum_fee >= urban_expend:
            max_year = max(years)
            final_fee = max_year * urban_expend
        else:
            final_fee = sum(fees_with_age)
        return final_fee


# 死亡赔偿
# 丧葬费
class FuneralFeeRule(Rule):

    name = '丧葬费'

    def __init__(self):
        self.region_salary = CalculatorModel().get_region_salary_map()

    def condition(self, params=None, **kwargs):
        return True

    def action(self, params=None, **kwargs):
        region = params.region
        try:
            salary = self.region_salary[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = salary * 6
        return fee


# 死亡补偿费
class DeathCompensationRuleA(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        # 城镇居民且受害人年龄≤60周岁
        if params.victim_is_urban and params.victim_age <= 60:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        try:
            income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * 20
        return fee


class DeathCompensationRuleB(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        # 城镇居民且受害人年龄60-75周岁
        if params.victim_is_urban and 60 < params.victim_age < 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        victim_age = params.victim_age
        try:
            income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * (20 - (victim_age - 60))
        return fee


class DeathCompensationRuleC(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_urban_income = CalculatorModel().get_region_urban_income_map()

    def condition(self, params=None, **kwargs):
        # 城镇居民且受害人年龄≥75周岁
        if params.victim_is_urban and params.victim_age >= 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        try:
            income = self.region_urban_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * 5
        return fee


class DeathCompensationRuleD(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        # 农村居民且受害人年龄≤60周岁
        if not params.victim_is_urban and params.victim_age <= 60:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * 20
        return fee


class DeathCompensationRuleE(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        # 农村居民且受害人年龄60-75周岁
        if not params.victim_is_urban and params.victim_age >= 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        victim_age = params.victim_age
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * (20 - (victim_age - 60))
        return fee


class DeathCompensationRuleF(Rule):

    name = '死亡补偿费'

    def __init__(self):
        self.region_rural_income = CalculatorModel().get_region_rural_income_map()

    def condition(self, params=None, **kwargs):
        # 农村居民且受害人年龄≥75周岁
        if not params.victim_is_urban and params.victim_age >= 75:
            return True

    def action(self, params=None, **kwargs):
        region = params.region
        try:
            income = self.region_rural_income[region]
        except KeyError:
            raise ArgumentTypeError('该地区未开通！')
        fee = income * 5
        return fee
