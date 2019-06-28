import json
import datetime
from questionaire.maintain_model import maintain_handler
from questionaire.tag_models import TagModel
from questionaire.base_model import BaseMongo
from microserver.utils import crypto
from microserver.utils.singleton import Singleton
from microserver.db.mongodb import MongoDB
from pymongo import UpdateOne


#通过案由id获取专题model
class TopicModel(MongoDB, Singleton):
    _name = "intelligent.topic"
    _alias_name = "intelligent"


#通过案由id获取纠纷类型名称
class Dispute_typeModel(MongoDB):
    _name = "intelligent.dispute_type"
    _alias_name = "intelligent"


#通过案由id和专题id获取第一个问题model
class QuestionDataModel(MongoDB):
    _name = "intelligent.question"
    _alias_name = "intelligent"

    def get_questions_by_choices(self, query_params,dispute_id,topic_id):
        huchi_tags = ['5c178ae4ba92937fb0af7922','5c178705ba92937fab837ea4','5c16f9b7ba929311d9b4594a',
                      '5c0f853dba92931ebca385ea','5c19f3b3ba92937015bc067e','5c19f62dba9293701341001e',
                      '5c19fce8ba92937018255812','5c1789c9ba92937faf5da691','5c17693eba92937fab837df9']
        #计算器唯一标识（给前端来判断调用那个计算器）
        death_type = ['5c1c7f9fba92936be387f793','5c18903aba92931aac81b162']
        disability_type=['5c1c7fb6ba92936be66ed34e','5c18901dba92931aa9cb0801']
        normalinjury_type=['5c1c837bba92936bea16859b','5c188ff7ba92931aa9cb07fd']
        dispute_model = Dispute_typeModel()
        topicmodel = TopicModel()
        dispute_data = dispute_model.find_one_by_query(query={'id':dispute_id})
        dispute_name = dispute_data['name']
        topic_data = topicmodel.find_one_by_query(query={'id':topic_id})
        subject_name = topic_data['name']
        cr = self.coll.aggregate([
            # {"$unwind": "$decide_tags"},
            {"$match": query_params}
        ])
        for c in cr:
            obj = self.dump(c)
            _types = []

            if obj["choice_type"] not in _types:
                _types.append(obj["choice_type"])
                obj.update({"choice_type_num": str(obj["choice_type"]) + str(_types.count(obj["choice_type"]))})
            else:
                _types.append(obj["choice_type"])
                obj.update({"choice_type_num": str(obj["choice_type"]) + str(_types.count(obj["choice_type"]))})
            if obj.get("choice_type") == 1 or obj.get("choice_type") == 2 or obj.get("choice_type") == 3 or obj.get("choice_type") == 4:
                temp_choice_tags = []
                for choice in obj.get("choice_tags"):
                    zh_name = choice['zh_name']
                    colloquial = choice['colloquial_description']
                    document = choice['document']
                    evidence = choice['evidence']
                    if colloquial != "":
                        pass
                    else:
                        colloquial = zh_name
                        document = ""
                        evidence = ""
                    if choice['tag_id'] in huchi_tags:
                        huchi = '1'
                    else:
                        huchi = '0'
                    if choice['tag_id'] in death_type:
                        calculator_type = "death"
                    elif choice['tag_id'] in disability_type:
                        calculator_type = "disability"
                    elif choice['tag_id'] in normalinjury_type:
                        calculator_type ='normalinjury'
                    else:
                        calculator_type = "0"
                    temp_choice_tags.append({"id": choice['tag_id'], "zh_name": zh_name, "colloquial": colloquial,
                                             "document": document, "evidence": evidence, 'huchi': huchi,'calculator_type':calculator_type})
                obj.update({"temp_choice_tags": temp_choice_tags,"case_cause":dispute_name,
                            "subject_id":obj['topic_id'],
                            "subject":subject_name,
                            "choice_type":str(obj['choice_type'])})
                del obj['topic_id']
                del obj['type_id']
                del obj['default_questions']
            return obj

    @staticmethod
    def has_combdoc(value: list) -> bool:
        for i in value:
            if i:
                break
        else:
            return True
        return False


#问卷选项记录model
class QuestionnaireRecordModel(BaseMongo, Singleton):
    _name = "intelligent.choice_record"
    _alias_name = "intelligent"

    @maintain_handler
    def create(self, vals, *args, **kwargs):
        cause_id = vals.get("cause_id")  # 案由id
        topic_id = vals.get("topic_id")  # 专题id
        choice_tags = vals.get("choice_tags")  # 选项ids
        qid = vals.get("qid")  # 问题id
        id = crypto.md5(str(datetime.datetime.now()))
        choices = [{"qid": qid, "choice_tags": choice_tags}]
        obj = dict(
            id=id,
            cause_id=cause_id,
            topic_id=topic_id,
            choices=choices
        )
        return super(QuestionnaireRecordModel, self).create(obj, **kwargs)


#通过案由id获取纠纷类型的id model
class DisputeModel(MongoDB):
    _name = "intelligent.dispute_type"
    _alias_name = "intelligent"


#组合文案model
class NewCombinationDocModel(MongoDB):
    _name = "intelligent.combination_document"
    _alias_name = "intelligent"
    def create(self,vals,*args,**kwargs):
        case_cause_id = vals.get("cause_id")  # 案由id
        subject_id = vals.get("topic_id")  # 专题id
        choices = vals.get("choices")  # 问题答案组合
        document = vals.get("document")  # 文案
        id = crypto.md5(str(datetime.datetime.now()))
        obj = dict(
            case_cause_id=case_cause_id,
            subject_id=subject_id,
            choices=choices,
            document=document
        )
        if self.get_count(query_params=obj):
            # raise self.exceptionlib.CustomException("已存在！")
            raise Exception("已存在！")
        else:
            obj.update({"id": id})
            return super(NewCombinationDocModel, self).create(obj, **kwargs)


from microserver.db.mysql import MySQL, Base, BaseMySQL, Column, CHAR, TEXT, \
    UniqueConstraint, Boolean, DateTime, Integer, BIGINT

# 标签-mysql model
class NewTagModel(Base, BaseMySQL):

    __tablename__ = "tag"
    __table_args__ = (
        {
            "mysql_engine": "InnoDB",
            "extend_existing": True,
        },
    )

    _name = "imonitor.%s" % __tablename__
    _alias_name = "hwmysql"

    id = Column(CHAR(length=255), primary_key=True, nullable=False)
    alias_name = Column(CHAR(length=255), nullable=True)
    colloquial_description = Column(TEXT, nullable=True)
    description = Column(TEXT, nullable=True)
    doc_keywords = Column(TEXT, nullable=True)
    document = Column(TEXT, nullable=True)
    exclude_keywords = Column(TEXT, nullable=True)
    keywords = Column(TEXT, nullable=True)
    zh_name = Column(CHAR(length=255), nullable=False)
    extract_method=Column(Integer,nullable=False)
    parse_type = Column(Integer,nullable=False)
    is_enable = Column(Integer, nullable=False)
    update_timestamp = Column(DateTime, nullable=False)

    def find_all(self, ids, **kwargs):
        session = kwargs.get("session") or self.get_session()()
        objects = []
        for id in ids:
            try:
                obj = session.query(self.__class__).filter(self.__class__.id == id).one()
            except:
                continue
            if session not in kwargs:
                session.close()
            find_one_result = {}
            for column in obj.__table__.columns.keys():
                find_one_result.update({column: getattr(obj, column)})
            if find_one_result["parse_type"]==2:
                objects.append(find_one_result)
        if not objects:
            return None
        return objects



class TagCliamModel(Base, BaseMySQL):

    __tablename__ = "tag_claim_relationship"
    __table_args__ = (
        {
            "mysql_engine": "InnoDB",
            "extend_existing": True,
        },
    )

    _name = "imonitor.%s" % __tablename__
    _alias_name = "hwmysql"

    id = Column(CHAR(length=24), primary_key=True, nullable=False)
    topic_id=Column(CHAR(length=24),nullable=False)
    tag_id=Column(CHAR(length=24),nullable=False)
    claim_id=Column(CHAR(length=24),nullable=False)
    update_timestamp=Column(DateTime, nullable=False)
    is_enable=Column(Integer, nullable=False)


# 公共文案model
class PublicDescModel(MongoDB):

    _name = "intelligent.public_desc"
    _alias_name = "intelligent"

    def find_one(self, ids, **kwargs):
        session = kwargs.get("session") or self.get_session()()
        objects = []
        for id in ids:
            obj = session.query(self.__class__).filter(self.__class__.id == id).one()
            if session not in kwargs and obj==[]:
                session.close()
            find_one_result = {}
            for column in obj.__table__.columns.keys():
                find_one_result.update({column: getattr(obj, column)})
            objects.append(find_one_result)
        if not objects:
            return None
        return objects

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

class Topic_tagModel(Base, BaseMySQL):
    __tablename__ = "tag_topic_relationship"
    __table_args__ = (
        {
            "mysql_engine": "InnoDB",
            "extend_existing": True,
        },
    )

    _name = "imonitor.%s" % __tablename__
    _alias_name = "hwmysql"

    id = Column(CHAR(length=24), primary_key=True, nullable=False)
    topic_id = Column(CHAR(length=24), nullable=False)
    tag_id = Column(CHAR(length=24), nullable=False)
    update_timestamp = Column(DateTime, nullable=False)
    is_enable = Column(Integer, nullable=False)