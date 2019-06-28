# @Time    : 2018/8/9
# @Author  : Dongrj

import datetime,json
from microserver.utils.singleton import Singleton
from microserver.db.mongodb import MongoDB
from microserver.cache.rediscache import RedisCache

class BaseMongo(MongoDB, Singleton):
    _name = None
    _alias_name = None

    def get_count(self, query_params):
        query_params.update(
            is_enable=True,
        )
        count = self.coll.find(query_params).count()
        return count

    def create(self,vals,*args,**kwargs):
        curr_time = str(datetime.datetime.now())
        vals["create_date"] = curr_time
        vals["write_date"] = curr_time
        vals["is_enable"] = True

        vals["maintain"] = [dict(
            operation_time = curr_time,
            user_name = self.get_username(*args, **kwargs),
            operation_type = "create",
        )]
        self.coll.insert_one(vals)
        return self.dump(vals)

    def update(self,vals,*args,**kwargs):
        query_params = kwargs.get("query_params") or {}
        if not query_params:
            # raise self.exceptionlib.CustomException("查询参数不能为空！")
            raise Exception("查询参数不能为空！")

        count = self.get_count(query_params)
        if count != 1:
            raise Exception("需要更新的数据个数：%s, 查询条件错误：%s！"%(count, query_params))

        query_params.update(dict(
            is_enable=True,
        ))
        cr = self.coll.find(query_params)
        curr_date = str(datetime.datetime.now())

        if not vals:
            # raise self.exceptionlib.CustomException("更新内容不能为空！")
            raise Exception("更新内容不能为空！")

        vals.update(dict(
            write_date=curr_date,
        ))
        for obj in cr:
            obj.update(vals)
            obj["maintain"] = obj.get("maintain") or []
            obj["maintain"].append(dict(
                operation_time=curr_date,
                user_name=self.get_username(*args, **kwargs),
                operation_type="update",
            ))
            obj["maintain"] = obj["maintain"][:1] + obj["maintain"][-1:]
            self.coll.save(obj)
        return self.dump(self.coll.find_one(query_params))

    def find_one(self, *args, **kwargs):
        # 检查查询参数
        if not "query_params" in kwargs:
            raise Exception("查询参数query_params不存在！")
        if not isinstance(kwargs.get("query_params"), dict):
            raise Exception("查询参数query_params:%s, 类型错误！"%kwargs.get("query_params"))
        if not kwargs.get("query_params"):
            raise Exception("查询参数query_params:%s, 不能为空！"%kwargs.get("query_params"))

        # 查询参数
        query_params = kwargs.get("query_params")
        query_params.update(dict(
            is_enable=True,
        ))
        obj = self.coll.find_one(query_params)
        if not obj:
            raise Exception("不存在:%s！"%query_params)
        return obj

    def get_username(self, *args, **kwargs):

        handler = kwargs.get("handler")
        if handler and hasattr(handler, "get_argument"):
            access_token = handler.get_argument('access_token', None)
            access_token_key = "oauth2_%s" % access_token
            # print("------test redis----{}".format(access_token_key))
            try:
                access_token_obj = json.loads(rediscache().get(access_token_key))
                user_name = access_token_obj.get("data")[0].get("realName") or "未知"
            except:
                user_name = "未知"
        else:
            user_name = "未知"
        return user_name

    def create_objectid(self,str=None):
        try:
            object_id = ObjectId(str)
        except:
            object_id = ''
        return object_id


class rediscache(RedisCache):
    alias_name = "redis_product"