from datetime import datetime
import json,requests
from questionaire.question_models import TopicModel
from microserver.core.handlers import handlers
from microserver.utils import decorator
from common import exceptionlib,logrelation
from questionaire.question_models import QuestionDataModel,QuestionnaireRecordModel,DisputeModel,NewCombinationDocModel,PublicDescModel
from questionaire.question_models import NewTagModel,TagCliamModel,ZNYSModel,Topic_tagModel
#重构获取专题接口
class GetTopicHandler(handlers.NoAuthHandler):
    """
@name 获取案由下的专题
@description 获取案由下的专题
@path
  /intelligentpretrial/znys/subjects:
    get:
      tags:
      - "获取案由下的专题"

      produces:
      - "application/json"

      parameters:
      - name: "cause_id"
        in: "query"
        description: "案由id"
        type: "string"
        required: true

      responses:
        200:
         description: "返回成功"
         schema:
            $ref: "#/definitions/Action"
        400:
          description: "返回失败"
@endpath

@definitions
  Action:
    type: "object"
    properties:
      data:
        type: "array"
        xml:
          wrapped: true
        items:
          $ref: "#/definitions/ActionContent"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  ActionContent:
    type: "object"
    properties:
      id:
        type: "string"
        description: "专题id"
      recommended_actions:
        type: "array"
        xml:
          wrapped: true
        items:
          type: "string"
          description: "行动建议"
      description:
        type: "string"
        description: "专题描述"
      is_online:
        type: "boolean"
        description: "是否上线，true为是，false为否"
      is_repet:
        type: "boolean"
        description: "案由和专题名字是否重复，true为是，false为否"
      has_calculator:
        type: "boolean"
        description: "是否有计算器"
      evidence:
        type: "string"
        description: "专题的证据"
      zh_name:
       type: "string"
       description: "专题的中文名称"

@enddefinitions
    """
    topicmodel = TopicModel()
    couseModel = DisputeModel()
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(GetTopicHandler, self).prepare()
        self.cause_id = self.get_argument("cause_id")

    @decorator.threadpoll_executor
    def get(self):

        result = self.init_response_data()
        cause_obj =  self.couseModel.find_one_by_query(query={"id":self.cause_id})
        cause_name = cause_obj['name']
        objs,pager = self.topicmodel.search(query={"type_id":self.cause_id,'is_enable':True})
        is_repet = False
        if cause_name == objs[0]['name']:
            is_repet=True
        list_obj = [
            {
                'description': obj['description'],
                'id': obj['id'],
                'zh_name': obj['name'],
                'recommended_actions':obj['recommended_actions'],
                'evidence':obj['evidence'],
                'is_online':obj['is_online'],
                'has_calculator':obj['has_calculator'],
                'is_repet':is_repet
            } for obj in objs
        ]
        result['data'] = list_obj
        return result


#重构获取专题下第一个问题接口
class NewGetFirstQuestion(handlers.NoAuthHandler):
    """
@name 取专题下第一个问题
@description 取专题下第一个问题
@path
  /intelligentpretrial/znys/first/question:
    post:
      tags:
      - "取专题下第一个问题"

      produces:
      - "application/form-data"

      parameters:
      - name: "cause_id"
        in: "query"
        description: "案由id"
        type: "string"
        required: true

      - name: "subject_id"
        in: "query"
        description: "专题id"
        type: "string"
        required: true

      responses:
        200:
          description: "返回成功"
          schema:
           $ref: "#/definitions/Aqtion"
        400:
          description: "返回失败"

@endpath

@definitions
  Aqtion:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/AqtionContent"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  AqtionContent:
    type: "object"
    properties:
      id:
        type: "string"
        description: "问题id"
      temp_choice_tags:
        type: "array"
        items:
          $ref: "#/definitions/Temp_tags"
      choice_type:
        type: "string"
        description: "问题类型，1为单选题，2为多选题"
      question:
        type: "string"
        description: "问题名称"

  Temp_tags:
    type: "object"
    properties:
      id:
        type: "string"
        description: "标签id"
      zh_name:
        type: "string"
        description: "标签中文名"
      colloquial:
        type: "string"
        description: "口语化描述"
      evidence:
        type: "string"
        description: "标签上的证据"
      document:
        type: "string"
        description: "标签上的文案"

@enddefinitions
    """
    Datamodel = QuestionDataModel()
    disputemodel = DisputeModel()
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(NewGetFirstQuestion, self).prepare()
        self.cause_id = self.get_argument("cause_id","")
        self.subject_id = self.get_argument("subject_id","")
    @decorator.threadpoll_executor
    def post(self):

        result = self.init_response_data()
        question_data = {}
        query_params = {
            "topic_id": self.subject_id,
            "is_first":True,
            "choice_type": {"$in": [1, 2]},
            'is_enable': True
        }
        questions = self.Datamodel.find_one_by_query(query=query_params)
        if questions:
            data_list = []
            for item in questions['choice_tags']:
                data_dict = {}
                data_dict['id'] = item['tag_id']
                data_dict['evidence'] = item['evidence']
                data_dict['document'] = item['document']
                data_dict['colloquial'] = item['colloquial_description']
                data_dict['zh_name'] = item['zh_name']
                data_list.append(data_dict)
            question_data['id'] = questions['id']
            question_data['temp_choice_tags'] = data_list
            question_data['choice_type'] = str(questions['choice_type'])
            question_data['question'] = questions['question']
        result['data'] = question_data
        return result


#重构获取下级问题接口
class NewGetNextQuestion(handlers.BaseHandler):
    """
@name 获取下级问题
@description 案由专题下根据选项查找下面的问题

@path
  /intelligentpretrial/znys/next/question:
    post:
      tags:
      - "获取下级问题"
      parameters:
      - name: "cause_id"
        in: "query"
        description: "案由id"
        type: "string"
        required: true
      - name: "subject_id"
        in: "query"
        description: "专题id"
        type: "string"
        required: true
      - name: "qid"
        in: "query"
        description: "问题id"
        type: "string"
        required: true
      - name: "tags"
        in: "query"
        description: "选项记录id"
        type: "array"
        items:
          type: "string"
        required: true
      - name: "answers"
        in: "query"
        description: "问题类型为3或4和5时的答案"
        type: "array"
        items:
          default: "[]"
        required: false
      - name: "record_id"
        in: "query"
        description: "选项记录id"
        type: "string"
        required: false

      responses:
        200:
          description: "返回成功"
          schema:
           $ref: "#/definitions/NextQue"
        400:
          description: "返回失败"
@endpath
@definitions
  NextQue:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/Question"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  Question:
    type: "object"
    properties:
      record_id:
        type: "string"
        description: "选项记录的id"
      questions:
        type: "array"
        items:
          $ref: "#/definitions/QueContent"
  QueContent:
    type: "object"
    properties:
      id:
        type: "string"
        description: "问题id"
      decide_tags:
        type: "array"
        items:
          default: "[]"
      case_cause:
        type: "string"
        description: "案由名称"
      choice_tags:
        type: "array"
        items:
          $ref: "#/definitions/Choicetags"
      _id:
        type: "string"
      choice_type:
        type: "string"
        description: "问题类型，1为单选，2为多选,3为填空，4为日期，5为地址"
      temp_choice_tags:
        type: "array"
        items:
          $ref: "#/definitions/TempChoicetags"
      subject_id:
        type: "string"
        description: "专题id"
      create_time:
        type: "string"
        description: "创建时间"
      choice_type_num:
        type: "string"
        description: "问题类型"
      document:
        type: "string"
        description: "文案"
      question:
        type: "string"
        description: "问题名称"
      write_time:
        type: "string"
      is_first:
        type: "boolean"
        description: "是否是首个问题"
        default: false
      subject:
        type: "string"
        description: "专题名称"
      is_enable:
        type: "boolean"
  Choicetags:
    type: "object"
    properties:
      weight:
        type: "integer"
        format: "int64"
        description: "标签权重"
      evidence:
        type: "string"
        description: "标签的证据"
      tag_id:
        type: "string"
        description: "标签id"
      zh_name:
        type: "string"
        description: "中文名称"
      document:
        type: "string"
        description: "标签的文案"
      colloquial_description:
        type: "string"
        description: "口语化描述"
  TempChoicetags:
    type: "object"
    properties:
      document:
        type: "string"
        description: "标签文案"
      id:
        type: "string"
        description: "标签id"
      evidence:
        type: "string"
        description: "标签证据"
      zh_name:
        type: "string"
        description: "中文名"
      huchi:
        type: "string"
        description: "标签互斥标识"
      colloquial:
        type: "string"
        description: "口语化描述"
@enddefinitions
    """
    questionmodel = QuestionDataModel()
    record_model = QuestionnaireRecordModel()

    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(NewGetNextQuestion, self).prepare()
        self.cause_id = self.get_argument("cause_id")
        self.subject_id = self.get_argument("subject_id")  # 专题id
        self.qid = self.get_argument("qid")  # 问题id
        self.tags = self.get_argument("tags")  # 选项的ids
        self.answers = self.get_argument("answers", "[]")  # 上面填空题答案
        self.record_id = self.get_argument("record_id", None)

    @decorator.threadpoll_executor
    def post(self):

        result = self.init_response_data()
        result['data'] = {}
        qid = self.qid
        record_id = self.record_id
        try:
            _obj = self.questionmodel.find_one_by_query(query={"id": qid})
        except:
            raise exceptionlib.CustomException("qid参数错误！")
        try:
            tags = json.loads(self.tags)
        except:
            raise exceptionlib.CustomException("tags参数类型错误！")
        if tags == []:
            tags = [""]
        try:
            answers = json.loads(self.answers)
        except:
            raise exceptionlib.CustomException("answers参数错误！")
        if _obj.get("choice_type") == "1" and len(tags) != 1:
            raise exceptionlib.CustomException("本题单选！")
        tags.sort()
        query_params = {"id":self.qid,
                        "topic_id": self.subject_id,
                        "$and": [],
                        "is_enable": True}
        for tag in tags:
            query_params['$and'].append({'decide_tags.combination':{'$elemMatch':{'tag_id':tag}}})

        present_question = self.questionmodel.find_one_by_query(query=query_params)
        questions = []
        if present_question:
            for qu in present_question['decide_tags']:
                for co in qu['combination']:
                    if tags[0] == co['tag_id']:
                        question = self.questionmodel.get_questions_by_choices(query_params={'id': qu['next_questions'][0]['qid']},
                                                                           dispute_id=self.cause_id,
                                                                           topic_id=self.subject_id)
                        questions.append(question)


        else:
            for item in _obj['default_questions']:
                question = self.questionmodel.get_questions_by_choices(query_params={'id': item['qid']},dispute_id=self.cause_id,topic_id=self.subject_id)
                questions.append(question)

        result['data']['questions'] = questions
        if record_id:#记录id不为空,则修改记录
            try:
                record = self.record_model.find_one(query_params={"id": record_id})
            except:
                raise exceptionlib.CustomException("record_id参数错误！")
            choices = record.get("choices") or []
            qids = [c.get('qid') for c in choices]
            if qid not in qids:
                if answers:
                    choices.extend(answers)
                choices.append({"qid": qid, "choice_tags": tags})
                self.record_model.update({"choices": choices}, query_params={"id": record_id}, handler=self)
            else:
                temp_choices = []
                for i in range(len(choices)):
                    if choices[i].get("qid") != qid:
                        temp_choices.append(choices[i])
                    else:
                        if answers:
                            temp_choices.extend(answers)
                        c = choices[i]
                        c.update({"choice_tags": tags})
                        temp_choices.append(c)
                        break
                self.record_model.update({"choices": temp_choices}, query_params={"id": record_id}, handler=self)
            result['data'].update({"record_id": record_id})
        else:  # 记录id为空,则新建记录
            obj = dict(
                cause_id=self.cause_id,
                topic_id=self.subject_id,
                choice_tags=tags,
                qid=qid,
            )
            record = self.record_model.create(obj, handler=self)
            result['data'].update({
                "record_id": record.get("id")
            })
        return result


#重构查询选项记录接口
class NewRecordChoice(handlers.NoAuthHandler):
    """
@name 查询选项记录
@description 查询选项记录

@path
  /intelligentpretrial/znys/choice_record:
    get:
      tags:
      - "查询选项记录"

      produces:
      - "application/json"

      parameters:
      - name: "qid"
        in: "query"
        description: "查询选项记录的id"
        type: "string"
        required: true
      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/Abtion"
        404:
          description: "返回失败"

@endpath

@definitions
  Abtion:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/legal"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  legal:
    type: "object"
    properties:
      legal_advice:
        type: "string"
        description: "法律意见"
      temp_tags:
        type: "array"
        items:
          $ref: "#/definitions/Tamp_tags"
      subject:
        type: "string"
        description: "专题名称"
      subject_id:
        type: "string"
        description: "专题id"
      case_cause_id:
        type: "integer"
        format: "int64"
        description: "案由id"
  Tamp_tags:
    type: "object"
    properties:
      choice_tags:
        type: "array"
        items:
          $ref: "#/definitions/Chiicetags"
      qid:
        type: "string"
        description: "问题id"
  Chiicetags:
    type: "object"
    properties:
      weight:
        type: "integer"
        format: "int64"
        description: "标签权重"
      evidence:
        type: "string"
        description: "标签证据"
      id:
        type: "string"
        description: "标签id"
      zh_name:
        type: "string"
        description: "中文名称"
      document:
        type: "string"
        description: "标签文案"
      colloquial_description:
        type: "string"
        description: "口语化描述"
@enddefinitions
    """
    model = QuestionnaireRecordModel()
    subject_model = TopicModel()
    combin_document_model = NewCombinationDocModel()
    public_descmodel = PublicDescModel()
    disputetypemodel = DisputeModel()

    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(NewRecordChoice, self).prepare()
        self.record_id = self.get_argument("record_id")

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):

        result = self.init_response_data()
        result['data'] = {}
        try:
            obj = self.model.find_one(query_params={"id": self.record_id})
        except Exception as e:
            print(e)
            raise exceptionlib.CustomException("%s不存在！" % self.record_id)
        case_cause_id = obj.get("cause_id")
        subject_id = obj.get("topic_id")
        qids = []
        tags=[]
        flag_choice_dict = {}
        for c in obj.get("choices"):
            qids.append(c["qid"])
            choice_tags = c.get('choice_tags')
            tags.extend(c.get("choice_tags", []))
            flag_choice_dict[c['qid']] = choice_tags if choice_tags else c.get('answer')
        answer = None

        # 保险合同纠纷
        if "5c1778beba92937fab837e7a" in qids:
            answer=obj.get('choices')[2]['answer']
            qids.remove('5c1778beba92937fab837e7a')
            qids.remove('5c1778beba92937fab837e7a')

        questions = QuestionDataModel().search_read(pager_flag=False, query_params={"id": {"$in": qids}},
                                                _project={"id": 1, "question": 1, "choice_tags": 1})[0]
        question_dict = {}
        for question in questions:
            question_dict[question["id"]] = question
        sorted_questions = []
        for qid in qids:
            sorted_questions.append(question_dict[qid])
        questions = sorted_questions


        final_result = []
        for question in questions:
            tmp_dict = {}
            tmp_dict['qid'] = question['id']
            tmp_dict['choice_tags'] = []
            choiced_id = flag_choice_dict[question['id']]
            for choice_id in choiced_id:
                for question_choice in question['choice_tags']:
                    try:

                        if choice_id == question_choice['tag_id']:
                            tmp_dict['choice_tags'].append({
                                "id": choice_id,
                                "zh_name":question_choice['zh_name'],
                                "colloquial_description":question_choice['colloquial_description'],
                                "document":question_choice['document'],
                                "weight":question_choice['weight'],
                                "evidence": question_choice['evidence'],
                            })
                    except:
                        pass
            final_result.append(tmp_dict)
        sub_des_obj = self.subject_model.find_one_by_query(
            query={"id": subject_id})
        subject_name = sub_des_obj.get("name", "")
        type_obj = self.disputetypemodel.find_one_by_query(query={"id": case_cause_id})
        type_id = type_obj.get("cause_id")
        result['data']['case_cause_id']=type_id
        result['data']['subject_id'] = subject_id
        result['data']['subject'] = subject_name
        result['data']['temp_tags'] = final_result
        public_qid = ['5c17619bba929379dd40fe9d', '5c18c335ba92931aa9cb094c',
                      '5c179175ba92937faf5da6da', '5c179282ba92937fab837ed9',
                      '5c1a05d7ba929370113bf72a'
                      ]
        public_desc_especial_id=['5c1ca9f8ba92936be66ed497']#有两个公共文案的特殊问题id
        #著作权纠纷特殊标签
        special_tags_id=['5c1ca182ba92936be66ed436','5c1ca2d2ba92936be5f1d072','5c1ca2faba92936be66ed440','5c1ca31bba92936be5f1d076']#
        document=[]
        for choice in final_result:
            if choice['qid'] in public_qid:
                public_doc = self.public_descmodel.find_one_by_query(query={'question_id': choice['qid']})
                gs = ''
                for tag_id in public_doc.get('options',[]):
                    if tag_id['tag_id'] in tags:
                        gs = gs + tag_id['name'] +'、'+'、'
                        gs = gs[:len(gs) - 1]
                gs = gs[:len(gs) - 1]
                document.append(public_doc['document'].replace('{}',gs))
            elif choice['qid'] in public_desc_especial_id:
                public_desc_obj = self.public_descmodel.find_one_by_query(query={'id':"5c20393bba92933dc8ed66dd"})
                ga = ''
                for tag_id in public_desc_obj.get('options', []):
                    if tag_id['tag_id'] in tags:
                        ga = ga + tag_id['name'] + '、'
                ga = ga[:len(ga) - 1]
                doc_usual=public_desc_obj['document'].replace('{}',ga)
                document.append(doc_usual)

                if "5c1ca182ba92936be66ed436" or "5c1ca2d2ba92936be5f1d072" or "5c1ca2faba92936be66ed440" or "5c1ca31bba92936be5f1d076" in special_tags_id:
                    public_desc_specal = self.public_descmodel.find_one_by_query(query={'id':"5c20386fba92933dbf515f3d"})
                    gc = ''
                    for tag_id_spe in public_desc_specal.get('options', []):
                        if tag_id_spe['tag_id'] in tags:
                            gc = gc + tag_id_spe['name'] + '、'
                    gc = gc[:len(gc) - 1]
                    doc_special=public_desc_specal['document'].replace('{}',gc)
                    document.append(doc_special)
                else:
                    pass

            else:
                for doc in choice["choice_tags"]:
                    if doc["document"]!="":
                        document.append(doc["document"])

        if case_cause_id == "5c1770b1ba92937fadd743a4":
            time_obj = datetime.strptime(answer, '%Y-%m-%d')
            now_time = datetime.now()
            delta = now_time - time_obj
            days = delta.days
            if "5c1772ecba92937fab837e56" in tags and days < 1825:
                combination_doc = "根据您的选择，发生争议的保险类型为人寿保险，其诉讼时效期间为五年，因此诉讼时效期间尚未届满，您可以向被告所在地法院提起诉讼。"
                document.insert(1,combination_doc)
            elif "5c1772ecba92937fab837e56" in tags and days>1825:
                combination_doc ="根据您的选择，发生争议的保险类型为人寿保险，其诉讼时效期间为五年。现在已超过诉讼时效，法院可能会判决驳回诉讼请求，对方可以不用赔付保险金。但如有证据证明，你不知道发生保险事故，则从您知道保险事故发生之日起计算；事故发生后，您与对方有进行调解、协商的，则从调解失败或协商失败之日起算。"
                document.insert(1, combination_doc)
            elif "5c20a0ecba92930e06d43685" in tags and days<730:
                combination_doc="根据您的选择，发生争议的保险类型为除人寿保险外的其他保险，其诉讼时效期间为两年，诉讼时效期间尚未届满，您可以向合同约定的争议解决法院提起诉讼。"
                document.insert(1, combination_doc)
            elif "5c20a0ecba92930e06d43685" in tags and days > 730:
                combination_doc ="根据您的选择，发生争议的保险类型为除人寿保险外的其他保险，其诉讼时效期间为两年。已超过诉讼时效，法院将会判决驳回诉讼请求。但是如有证据证明，您不知道发生保险事故，则从您知道保险事故发生之日起计算；事故发生后，您与对方有进行调解、协商的，则从调解失败或协商失败之日起算。"
                document.insert(1, combination_doc)
        elif case_cause_id=="5c13548aba929311d0fbfc4d":
            if "5c1b6727ba92936be66ed299"==tags[0] and "5c1b686dba92936bea1684f0"==tags[1] and "5c1c4742ba92936be387f73d"==tags[3]:
                combination_doc ="您驾驶的机动车与非机动车发生交通事故的，非机动车驾驶人负事故全部责任的，通常由机动车一方承担不超过10%的赔偿责任。非机动车驾驶人、行人与处于静止状态的机动车发生交通事故，机动车一方无交通事故责任的，不承担赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1c3c57ba92936bea16851b"==tags[1] and "5c1c4742ba92936be387f73d"==tags[3]:
                combination_doc ="您驾驶的机动车与行人发生交通事故的，行人负事故全部责任的，通常由机动车一方承担不超过10%的赔偿责任。非机动车驾驶人、行人与处于静止状态的机动车发生交通事故，机动车一方无交通事故责任的，不承担赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1b686dba92936bea1684f0"==tags[1] and "5c1c47a5ba92936bea16854e"==tags[3]:
                combination_doc="您驾驶的机动车与非机动车发生交通事故，非机动车驾驶人负事故主要责任的，机动车一方负次要责任的，由非机动车承担主要的赔偿，由于您也存在过错，故而您需要承担部分赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1b686dba92936bea1684f0"==tags[1] and "5c1c4839ba92936be387f742"==tags[3]:
                combination_doc="您驾驶的机动车与非机动车发生交通事故，事故双方负同等责任的，由双方各自承担相应的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1c3c57ba92936bea16851b"==tags[1] and "5c1c47a5ba92936bea16854e"==tags[3]:
                combination_doc="您驾驶的机动车与行人发生交通事故，行人负事故主要责任的，机动车一方负次要责任的，由行人承担主要的赔偿，由于您也存在过错，故而您需要承担部分赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1c3c57ba92936bea16851b"==tags[1] and "5c1c4839ba92936be387f742"==tags[3]:
                combination_doc="您驾驶的机动车与行人发生交通事故，事故双方负同等责任的，由双方各自承担相应的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1b686dba92936bea1684f0"==tags[1] and "5c1c4861ba92936be5f1cf70"==tags[3]:
                combination_doc="您驾驶的机动车与非机动车发生交通事故，机动车人负事故的主要责任，非机动车负事故次要责任的，需要由您承担主要的赔偿，非机动车只承担次要的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1c3c57ba92936bea16851b"==tags[1] and "5c1c4861ba92936be5f1cf70"==tags[3]:
                combination_doc="您驾驶的机动车与行人发生交通事故，机动车人负事故的主要责任，行人负事故次要责任的，需要由您承担主要的赔偿，非机动车只承担次要的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1b686dba92936bea1684f0"==tags[1] and "5c1c4997ba92936be66ed300"==tags[3]:
                combination_doc="您驾驶的机动车与非机动车发生交通事故的，机动车人负事故的全部责任，非机动车无事故责任的，通常由机动车一方承担全部赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1c3c57ba92936bea16851b"==tags[1] and "5c1c4997ba92936be66ed300"==tags[3]:
                combination_doc="您驾驶的机动车与非机动车发生交通事故的，机动车人负事故的全部责任，非机动车无事故责任的，通常由机动车一方承担全部赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b686dba92936bea1684f0"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4742ba92936be387f73d"==tags[3]:
                combination_doc= "您驾驶的非机动车与机动车发生交通事故，机动车负全部责任，应当动车无事故责任的，通常由机动车一方承担全部赔偿责任，您无需承担赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b686dba92936bea1684f0"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c47a5ba92936bea16854e"==tags[3]:
                combination_doc="您驾驶的非机动车与机动车发生交通事故，机动车负主要责任，非机动车负次要责任的，应当由机动车一方承担主要赔偿，由于您对事故的发生也存在过错，故而您需要承担部分赔偿。"
                document.insert(1, combination_doc)
            elif "5c1b686dba92936bea1684f0"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4839ba92936be387f742"==tags[3]:
                combination_doc="您驾驶的非机动车与机动车发生交通事故，事故双方负同等责任的，由双方各自承担相应的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b686dba92936bea1684f0"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4861ba92936be5f1cf70"==tags[3]:
                combination_doc= "您驾驶的非机动车与机动车发生交通事故，非机动车负主要责任，机动车负次要责任的，应当由您承担主要赔偿，机动车只承担次要的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b686dba92936bea1684f0"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4997ba92936be66ed300"==tags[3]:
                combination_doc="机动车与非机动车发生交通事故的，非机动车驾驶人负事故全部责任的，由机动车一方承担不超过10%的赔偿责任。非机动车驾驶人与处于静止状态的机动车发生交通事故，机动车一方无交通事故责任的，不承担赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1c3c57ba92936bea16851b"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4742ba92936be387f73d"==tags[3]:
                combination_doc= "您与机动车发生交通事故，机动车负全部责任，行人无事故责任的，通常由机动车一方承担全部赔偿责任，您无需承担赔偿。"
                document.insert(1, combination_doc)
            elif "5c1c3c57ba92936bea16851b" and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c47a5ba92936bea16854e"==tags[3]:
                combination_doc= "您与机动车发生交通事故，机动车负主要责任，行人负次要责任的，应当由机动车一方承担主要赔偿，由于您对事故的发生也存在过错，故而您需要承担部分赔偿。"
                document.insert(1, combination_doc)
            elif "5c1c3c57ba92936bea16851b"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4839ba92936be387f742"==tags[3]:
                combination_doc="您与机动车发生交通事故，事故双方负同等责任的，由双方各自承担相应的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1c3c57ba92936bea16851b"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4861ba92936be5f1cf70"==tags[3]:
                combination_doc= "您与机动车发生交通事故，行人负主要责任，机动车负次要责任的，应当由您承担主要赔偿，机动车只承担次要的赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1c3c57ba92936bea16851b"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] and "5c1c4997ba92936be66ed300"==tags[3]:
                combination_doc= "机动车与行人发生交通事故的，行人负事故全部责任的，由机动车一方承担不超过10%的赔偿责任。行人与处于静止状态的机动车发生交通事故，机动车一方无交通事故责任的，不承担赔偿责任。"
                document.insert(1, combination_doc)
            elif "5c1b6727ba92936be66ed299"==tags[0] and "5c1b6727ba92936be66ed299"==tags[1] in tags:
                combination_doc ="对于双方都是机动车的交通事故案件，由负全责的一方承担损害赔偿责任；双方对事故的发生均有责任的，按照各自的过错比例承担赔偿责任。"
                document.insert(0, combination_doc)
        elif case_cause_id == "5c16f789ba929311d0fbfc7e":
            if "5c16fd32ba929311d9b45979" or "5c16fd4bba929311d9b4597f" or "5c16fd78ba929311d9b45987" in tags:
                combination_doc = "对父母、子女、兄弟姐妹等家庭成员共同生活、共同劳动，如用劳动所得建造的房屋、添置的生活、生产资料；家庭成员长期共同管理、共同使用的祖遗财产；共同出资购买的房屋等属于家庭共有的财产进行“分家”，才是法律意义上的“析产”。"
                document.insert(-1, combination_doc)
        else:
            pass
        final_document = "\n".join(document)
        #未签劳动合同 文案由计算器得出
        if subject_id == "5c175f52ba929379dd40fe81":
            final_document=""

        result['data']['legal_advice'] =final_document
        return result


class TopicEvidenceHangdler(handlers.NoAuthHandler):
    """
@name 获取证据
@description 获取证据

@path
  /intelligentpretrial/android/law_push/evidence:
    get:
      tags:
      - "获取证据"

      produces:
      - "application/json"

      parameters:
      - name: "topic_id"
        in: "query"
        description: "专题id"
        type: "string"
        required: true
      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/DataOfevidence"
        404:
          description: "返回失败"
@endpath
@definitions
  DataOfevidence:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/Evdence"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  Evdence:
    type: "object"
    properties:
      evidence:
        type: "string"
        description: "专题证据"
@enddefinitions
    """
    topicmodel = TopicModel()
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(TopicEvidenceHangdler, self).prepare()
        self.topic_id = self.get_argument("topic_id", '')

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        subject_obj = self.topicmodel.find_one_by_query(query={"id":self.topic_id})
        evidence={}
        evidence["evidence"] = subject_obj['evidence']
        result['data'] = evidence
        return result


class NewSelectAppeal(handlers.NoAuthHandler):

    """
@name 诉求选择
@description 诉求选择

@path
  /intelligentpretrial/android/law_push/selectclaim:
    get:
      tags:
      - "诉求选择"

      produces:
      - "application/json"

      parameters:
      - name: "qid"
        in: "query"
        description: "查询选项记录的id"
        type: "string"
        required: true
      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/DataOfmsg"
        404:
          description: "返回失败"
@endpath
@definitions
  DataOfmsg:
    type: "object"
    properties:
      data:
        type: "array"
        items:
          type: "string"
          description: "诉求名称"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
@enddefinitions
    """
    znysmodel = ZNYSModel()
    tag_claim_model = TagCliamModel()
    tag_model = NewTagModel()
    tag_topic=Topic_tagModel()
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(NewSelectAppeal, self).prepare()
        self.qid = self.get_argument("qid", '')

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        Choice_obj = self.znysmodel.find_one_by_query(query={'id':self.qid})
        choices=Choice_obj.get("choices")
        subject_id = self.znysmodel.get_subject_id(self.qid)
        tags = []
        for c in choices:
            tags.extend(c.get("choice_tags", []))
        if subject_id == "5c18995fba92931aa9cb088a":#承揽合同纠纷
            if len(choices) > 5 and choices[1].get("choice_tags", [])[0] == '5c189aeaba92931aac81b1f3':
                claimlist = self.get_claim(id='5c189aeaba92931aac81b1f3', subject_id=subject_id)
                result['data'] = claimlist
            elif len(choices) > 5 and choices[1].get("choice_tags", [])[0]== '5c189b95ba92931aac81b1f5':
                claimlist = self.get_claim(id='5c189b95ba92931aac81b1f5', subject_id=subject_id)
                result['data'] = claimlist
        elif subject_id == "5c18475bba92937fab837eff":#房屋租赁合同纠纷
            choice_tags_flag = 0  # 出租人
            if len(choices) > 1 and choices[0].get("choice_tags", [])[0]== '5c18486eba92937fb0af797b':
                choice_tags_flag = 1  # 承租人
            if choice_tags_flag == 0:
                claimlist = self.get_claim(id='5c184897ba92937fb0af797d', subject_id=subject_id)# 出租人
                result['data'] = claimlist
            else:
                claimlist = self.get_claim(id='5c18486eba92937fb0af797b', subject_id=subject_id)# 承租人
                result['data'] = claimlist
        elif subject_id == "5c177d11ba92937fab837e8d":#农村土地承包合同纠纷
            if len(choices) > 5 and choices[1].get("choice_tags", [])[0]== '5c1785acba92937fb0af7909':
                claimlist=self.get_claim(id='5c1785acba92937fb0af7909',subject_id=subject_id)
                result['data'] = claimlist
            elif len(choices) > 4 and choices[1].get("choice_tags", [])[0] == '5c17852aba92937fab837e97':
                claimlist = self.get_claim(id='5c17852aba92937fab837e97', subject_id=subject_id)
                result['data'] = claimlist
            else:
                claimlist = ['请求判令支付承包费', '请求判令支付违约金', '请求判令赔偿损失', '请求判令解除土地承包协议、合同', '请求判令土地承包合同无效', '请求判令退还土地','请求判令返还承包费']
                result['data'] = claimlist
        elif subject_id == "5c18a671ba92931aac81b265":#物业合同纠纷
            if choices[0].get("choice_tags", [])[0]== '5c19da3cba9293701825574b':#业主
                claimlist = self.get_claim(id='5c19da3cba9293701825574b', subject_id=subject_id)
                result['data'] = claimlist
            elif choices[0].get("choice_tags", [])[0]== '5c25cafcba929304cff14062':#物业服务公司
                claimlist = self.get_claim(id='5c25cafcba929304cff14062', subject_id=subject_id)
                result['data'] = claimlist

        else:
            tag_topic_obj, pager = self.tag_topic.search(query={'topic_id': subject_id},page=1,page_size=100)
            tags_list =[tag_obj['tag_id'] for tag_obj in tag_topic_obj]
            tag_obj=self.tag_model.find_all(ids=tags_list)
            claimlist = [claim_obj['zh_name'] for claim_obj in tag_obj]
            claim_set = set(claimlist)
            final_claim = list(claim_set)
            result["data"] = final_claim
        return result

    def get_claim(self,id,subject_id):

        tag_topic_obj, pager = self.tag_claim_model.search(
            query={'topic_id': subject_id, 'tag_id': id})
        claim_ids = [cli['claim_id'] for cli in tag_topic_obj]
        tag_obj = self.tag_model.find_all(ids=claim_ids)
        claimlist = [claim_obj['zh_name'] for claim_obj in tag_obj]
        return claimlist

handlers = [
    (r"/intelligentpretrial/znys/first/question", NewGetFirstQuestion),
    (r"/intelligentpretrial/znys/next/question", NewGetNextQuestion),
    (r"/intelligentpretrial/znys/subjects", GetTopicHandler),
    (r"/intelligentpretrial/znys/choice_record", NewRecordChoice),
    (r"/intelligentpretrial/android/law_push/selectclaim", NewSelectAppeal),
    (r"/intelligentpretrial/android/law_push/evidence", TopicEvidenceHangdler)
]

