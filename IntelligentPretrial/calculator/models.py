# @Time    : 2018/7/13
# @Author  : Dongrj
from microserver.utils.singleton import Singleton
from microserver.db.mongodb import MongoDB


class ZNYSModel(MongoDB, Singleton):
    _name = "intelligent.choice_record"
    _alias_name = "intelligent"

    def update_record(self, body, qid):
        try:
            user_obj = self.coll.find_one({"id": qid})
            user_obj.update({"labor": body})
            self.coll.save(user_obj)
            return True
        except Exception as err:
            print('插入数据错误', err)
            return False
