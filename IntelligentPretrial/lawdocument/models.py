# @Time    : 2018/7/13
# @Author  : Dongrj
from microserver.utils.singleton import Singleton
from microserver.db.mongodb import MongoDB


class ZNYSModel(MongoDB, Singleton):
    _name = "intelligent.choice_record"
    _alias_name = "intelligent"

    def get_labor(self, qid):
        try:
            user_obj = self.coll.find_one({"id": qid})
            _re = user_obj.get('labor', {})
            return _re
        except:
            return {}

    def get_choices(self, qid):
        try:
            user_obj = self.coll.find_one({"id": qid})
            choices = user_obj.get('choices', [])
            return choices
        except:
            return []

    def get_subject_id(self, qid):
        try:
            user_obj = self.coll.find_one({"id": qid})
            _re = user_obj.get('topic_id', '')
            return _re
        except:
            return ''


class ZNYSARModel(MongoDB, Singleton):
    _name = "tag.subject_description"
    _alias_name = "mongodb"


    def get_recommended_actions(self, qid):
        try:
            user_obj = self.coll.find_one({"subject_id": qid})
            _re = user_obj.get('recommended_actions', [])
            return _re
        except:
            return {}


#生成起诉状model
class IndictmentModel(MongoDB, Singleton):
    _name = "intelligent.indictment"
    _alias_name = "intelligent"


#选项记录model
class Choice_recordModel(MongoDB, Singleton):
    _name = "intelligent.choice_record"
    _alias_name = "intelligent"

    def get_subject_id(self, qid):
        try:
            user_obj = self.coll.find_one({"id": qid})
            _re = user_obj.get('topic_id', '')
            return _re
        except:
            return ''


class Topic_recommendModel(MongoDB, Singleton):
    _name = "intelligent.topic"
    _alias_name = "intelligent"

    def get_recommended_actions(self, qid):
        try:
            user_obj = self.coll.find_one({"topic_id": qid})
            _re = user_obj.get('recommended_actions', [])
            return _re
        except:
            return {}


