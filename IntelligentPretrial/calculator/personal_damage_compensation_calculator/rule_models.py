#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ZhangXiaocheng
# @File: rule_models.py
# @Time: 2019/1/9 18:45


from datetime import datetime
from microserver.db.mysql import Base, BaseMySQL, Column, CHAR, Integer


class CalculatorModel(Base, BaseMySQL):

    __tablename__ = "calculator_statistics"
    __table_args__ = (
        {
            "mysql_engine": "InnoDB",
            "extend_existing": True,
        },
    )

    _name = "tag.%s" % __tablename__
    _alias_name = "mysql"

    id = Column(Integer, primary_key=True, nullable=False)
    region = Column(CHAR(length=20), nullable=False)
    year = Column(Integer, nullable=True)
    value = Column(Integer, nullable=False, default=0)
    type = Column(CHAR(length=20), nullable=False)
    detail = Column(CHAR(length=20), nullable=True, default='')

    def get_all(self):
        return self.search({}, page=1, page_size=100)[0]

    def get_region_salary_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '职工月平均工资'
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_salary = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_salary

    def get_region_standard_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '出差伙食补助标准'
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_standard = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_standard

    def get_region_urban_income_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '城镇',
            'detail': '城镇居民人均年可支配收入',
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_urban_income = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_urban_income

    def get_region_rural_income_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '农村',
            'detail': '农村居民人均年纯收入',
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_rural_income = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_rural_income

    def get_region_urban_expend_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '城镇',
            'detail': '城镇居民人均年消费性支出',
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_urban_expend = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_urban_expend

    def get_region_rural_expend_map(self):
        current_year = datetime.now().year
        last_year = current_year - 1
        query = {
            'year': last_year,
            'type': '农村',
            'detail': '农村居民人均年消费性支出',
        }
        objs = self.search(query=query, page=1, page_size=50)[0]
        region_rural_expend = {
            obj['region']: obj['value'] for obj in objs if obj['value'] != 0
        }
        return region_rural_expend

    @staticmethod
    def supported_alimoney(coef, urban_expend, rural_expend, supporteds):
        """
        :param coef: 伤残系数
        :param urban_expend: 城镇支出
        :param rural_expend: 农村支出
        :param supporteds: 被扶养人信息
        :return:
        """
        fees = []
        fees_with_age = []
        years = []
        for supported in supporteds:
            num_of_supporter = supported['num_of_supporter']
            urban = supported['supported_is_urban']
            age = supported['supported_age']
            no_income = supported['supported_no_income']
            if urban:
                fee = int(urban_expend / num_of_supporter * coef)
            else:
                fee = int(rural_expend / num_of_supporter * coef)
            if age < 18:
                fees.append(fee)
                fee_with_age = fee * (18 - age)
                fees_with_age.append(fee_with_age)
                years.append(18 - age)
            elif 18 <= age <= 60 and no_income:
                fees.append(fee)
                fee_with_age = fee * 20
                fees_with_age.append(fee_with_age)
                years.append(20)
            elif 18 <= age <= 60 and not no_income:
                fees.append(0)
                fee_with_age = 0
                fees_with_age.append(fee_with_age)
            elif 60 < age < 75:
                fees.append(fee)
                fee_with_age = fee * (20 - (age - 60))
                fees_with_age.append(fee_with_age)
                years.append(20 - (age - 60))
            elif age >= 75:
                fees.append(fee)
                fee_with_age = fee * 5
                fees_with_age.append(fee_with_age)
                years.append(5)
        return fees, fees_with_age, years
