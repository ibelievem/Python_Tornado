#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/4 12:28
# @Author  : Niyoufa
# @Site    : 
# @File    : models111.py.py
# @Software: PyCharm

import json
import datetime
import traceback
from questionaire.base_model import BaseMongo
from questionaire import utils
from microserver.utils.singleton import Singleton

class MaintainModel(BaseMongo, Singleton):
    _name = "server.maintain"
    _alias_name = "mongodb"

    def create(self,vals,*args,**kwargs):
        if not isinstance(vals, dict):
            raise Exception("vals参数类型错误！")
            # raise self.exceptionlib.CustomException("vals参数类型错误！")

        if (not "operation_id" in vals) and (not "query_params" in vals):
            raise Exception("operation_id参数和query_params参数不能都为空！")
        if not "operation_coll" in vals:
            raise Exception("operation_coll参数不能为空！")
        if not "operation_type" in vals:
            raise Exception("operation_type参数不能为空！")

        operation_coll = vals.get("operation_coll")
        operation_id = vals.get("operation_id")
        query_params = vals.get("query_params")
        operation_type = vals.get("operation_type")
        operation_info = vals.get("operation_info")
        user_name = vals.get("user_name")

        curr_time = str(datetime.datetime.now())
        operation_time = curr_time

        obj = dict(
            operation_coll = operation_coll,
            operation_type=operation_type,
            operation_id = operation_id,
            query_params = query_params,
            operation_info = operation_info,
            user_name = user_name,
            operation_time = operation_time
        )
        self.coll.insert_one(obj)

def maintain_handler(operation_func):
    def maintain_operation(self,*args,**kwargs):
        operation_obj = operation_func(self, *args, **kwargs)
        operation_obj = MaintainModel().dump(operation_obj)
        try:
            operation_coll = self._name
            operation_type = operation_func.__name__
            maintain_vals = dict(
                operation_coll = operation_coll,
                operation_type = operation_type,
            )
            if operation_type == "create":
                operation_id = operation_obj.get("_id")
                maintain_vals.update(dict(
                    operation_id = operation_id,
                ))
            elif operation_type == "update":
                query_params = kwargs.get("query_params")
                maintain_vals.update(dict(
                    query_params = json.dumps(query_params),
                ))
            operation_info = args[0]
            maintain_vals.update(dict(
                operation_info = operation_info,
                user_name = self.get_username(*args, **kwargs)
            ))
            MaintainModel().create(maintain_vals)
            return operation_obj
        except Exception as err:
            try:
                info = traceback.format_exc()
                utils.api_log(info)
            except:
                pass
    return maintain_operation
