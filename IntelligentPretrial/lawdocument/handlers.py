# @Time    : 2018/7/13
# @Author  : Dongrj
from tornado import gen
from tornado.escape import utf8
from microserver.core.handlers import handlers
from microserver.utils import decorator
from microserver.utils import crypto
from microserver.conf import settings
from .models import ZNYSModel,Choice_recordModel,Topic_recommendModel
from lawdocument.mail import send_email
import requests
import json
import datetime,time
import os
import pypandoc
import random

from elasticsearch import Elasticsearch
import certifi
es_server = ['web.aegis-info.com:9200', 'web2.aegis-info.com:9200']
es = Elasticsearch(
    es_server,
    http_auth=('aegis', 'shield'),
    verify_certs=True,
    ca_certs=certifi.where(),
    timeout=60,
    sniff_on_start=True,
    sniff_on_connection_fail=True,
    sniffer_timeout=60
)


class ZNYS_SSS_Handler(handlers.BaseHandler):
    """
@name 生成起诉状
@description 生成起诉状
@path
  /intelligentpretrial/android/law_push/ZNYS_SSS_Handler:
    get:
      tags:
      - "生成起诉状"

      parameters:
      - name: "json_str"
        in: "body"
        schema:
            $ref: "#/definitions/JsonStr"
      - name: "qid"
        in: "query"
        description: "选项记录id"
        type: "string"
        required: true

      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/QiData"
        400:
          description: "返回失败"
@endpath

@definitions
  QiData:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/Answer"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  Answer:
    type: "object"
    properties:
      answer:
        type: "string"
        description: "起诉状模板"
  JsonStr:
    type: "object"
    properties:
      type:
        type: "integer"
        description: "原告类型"
      wttype:
        type: "integer"
        description: "委托代理人类型"
      plaintiff_name:
        type: "string"
        description: "原告自然人姓名"
      plaintiff_sex:
        type: "string"
        description: "原告自然人性别"
      plaintiff_ethnic:
        type: "string"
        description: "原告自然人民族"
      plaintiff_birth:
        type: "string"
        description: "原告自然人出生日期"
      plaintiff_ID_number:
        type: "string"
        description: "原告自然人身份证号"
      plaintiff_cellphone:
        type: "string"
        description: "原告自然人联系电话"
      plaintiff_address:
        type: "string"
        description: "原告自然人住处"
      plaintiff_company_name:
        type: "string"
        description: "原告法人名字"
      plaintiff_company_address:
        type: "string"
        description: "原告法人地址"
      plaintiff_company_legal_representative:
        type: "string"
        description: "原告法人代表名称及职务"
      plaintiff_attorney_name:
        type: "string"
        description: "原告委托代理人自然人的名字"
      plaintiff_attorney_sex:
        type: "string"
        description: "原告委托代理人自然人的性别"
      plaintiff_attorney_company:
        type: "string"
        description: "原告委托代理人自然人工作单位"
      plaintiff_attorney_address:
        type: "string"
        description: "原告委托代理人自然人住处"
      plaintiff_lawyer_name:
        type: "string"
        description: "原告委托代理人律师姓名"
      plaintiff_lawyer_office:
        type: "string"
        description: "原告委托代理人律师事务所"
      plaintiff_lawyer_telephone_number:
        type: "string"
        description: "原告委托代理人律师事务所电话"
      defendant_attorney_name:
        type: "string"
        description: "被告委托代理人自然人姓名"
      defendant_attorney_sex:
        type: "string"
        description: "被告委托代理人自然人性别"
      defendant_attorney_ethnic:
        type: "string"
        description: "被告委托代理人自然人民族"
      defendant_attorney_birth:
        type: "string"
        description: "被告委托代理人自然人出生日期"
      defendant_attorney_ID_number:
        type: "string"
        description: "被告委托代理人自然人身份证号"
      defendant_cellphone:
        type: "string"
        description: "被告自然人联系电话"
      defendant_attorney_address:
        type: "string"
        description: "被告委托代理人自然人住处"
      defendant_lawyer_name:
        type: "string"
        description: "被告委托代理人律师姓名"
      defendant_lawyer_office:
        type: "string"
        description: "被告委托代理人律师事务所名称"
      defendant_lawyer_address:
        type: "string"
        description: "被告委托代理人事务所地址"
      defendant_lawyer_telephone_number:
        type: "string"
        description: "被告委托代理人律师事务所电话"
      defendant_name:
        type: "string"
        description: "被告自然人姓名"
      defendant_sex:
        type: "string"
        description: "被告自然人性别"
      defendant_ethnic:
        type: "string"
        description: "被告自然人民族"
      defendant_birth:
        type: "string"
        description: "被告自然人出生日期"
      defendant_ID_number:
        type: "string"
        description: "被告自然人身份证号"
      defendant_address:
        type: "string"
        description: "被告自然人住处"
      defendant_attorney_company:
        type: "string"
        description: "被告被告自然人工作单位"
      defendant_company_name:
        type: "string"
        description: "被告法人名字"
      defendant_company_address:
        type: "string"
        description: "被告法人住处"
      defendant_company_legal_representative:
        type: "string"
        description: "被告法人法定代表人名称及职务"
      facts_and_reason:
        type: "string"
        description: "当事人补充的事实"
      claims:
        type: "array"
        items:
          type: "string"
          description: "诉讼请求"
@enddefinitions
    """
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(ZNYS_SSS_Handler, self).prepare()
        self.json_str = self.get_argument("json_str", '')
        self.qid = self.get_argument("qid", '')
        self.flag = int(self.get_argument("flag", '1'))

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        result['data'] = {}
        if self.flag == 1:
            _json_str = json.loads(self.json_str)
            answer = self.get_znys_sss(_json_str, self.qid)
            result['data']['answer'] = answer
            return result
        elif self.flag == 2:
            result['data']['answer'] = self.get_apply_arbitration(self.qid)
            return result

    def get_apply_arbitration(self, qid):
        re_ = True
        try:
            answer_ = requests.get('http://lmfy.assess.aegis-info.com/intelligentpretrial/znys/choice_record?record_id=%s' % (qid))
            choices = json.loads(answer_.text).get('data', {}).get('temp_tags', [])
            if choices[1].get("choice_tags", [])[0].get(
                    'id')=='5c10d794ba92931ec02947db':
                re_ = False
            elif choices[1].get("choice_tags", [])[0].get(
                    'id')=='5c10d759ba92931ec1c6c8a7':
                re_ = True
        except:
            pass
        return re_

    def get_znys_sss(self, json_str, qid):
        znysmodel = ZNYSModel()
        labor = znysmodel.get_labor(qid)
        subject_id = znysmodel.get_subject_id(qid)
        choices = znysmodel.get_choices(qid)
        re_str = ''
        if subject_id in ['5c0f6a29ba92931ec02947c1', '5c175f52ba929379dd40fe81']:
            if subject_id == '5c0f6a29ba92931ec02947c1':  # 离婚
                claims_str = ''
                jj = 1
                try:
                    answer_ = requests.get('http://lmfy.assess.aegis-info.com/intelligentpretrial/znys/choice_record?record_id=%s' % (qid))
                    choices = json.loads(answer_.text).get('data', {}).get('temp_tags', [])
                    if len(choices) > 0:
                        choices_0 = choices[0].get('choice_tags', [])
                        for ii in choices_0:
                            zh_name = ii.get('colloquial', '')
                            if zh_name != '':
                                claims_str = claims_str + '　　' + str(jj) + '、' + zh_name + '；\n'
                                jj = jj + 1
                except Exception as err:
                    print(err)
                    pass
                suqiu = json_str.get('claims', [])
                for item in suqiu:
                    claims_str = claims_str + '　　' + str(jj) + '、' + item + '；\n'
                    jj = jj + 1
                claims_str = claims_str + '　　' + str(jj) + '、请求被告承担诉讼费。\n'

                key_str = "plaintiff_name,plaintiff_sex,plaintiff_ethnic,plaintiff_birth,plaintiff_ID_number,plaintiff_address,plaintiff_cellphone," \
                          "plaintiff_company_name,plaintiff_company_address,plaintiff_company_legal_representative,plaintiff_attorney_name,plaintiff_attorney_sex," \
                          "plaintiff_attorney_ethnic,plaintiff_attorney_ID_number,plaintiff_attorney_birth,plaintiff_attorney_address," \
                          "plaintiff_lawyer_name,plaintiff_lawyer_address,plaintiff_lawyer_office,plaintiff_lawyer_telephone_number," \
                          "defendant_name,defendant_sex,defendant_ethnic,defendant_birth,defendant_ID_number,defendant_address," \
                          "defendant_company_name,defendant_company_address,defendant_company_legal_representative," \
                          "defendant_attorney_name,defendant_attorney_sex,defendant_attorney_ethnic,defendant_attorney_birth," \
                          "defendant_telephone,defendant_attorney_ID_number,defendant_attorney_address,defendant_cellphone," \
                          "defendant_lawyer_name,defendant_lawyer_office,defendant_lawyer_address,defendant_lawyer_telephone," \
                          "claims,facts_and_reason,facts_and_reason1，court_name,date"
                text_lh = """<h3 style="text-align: center;">民事起诉状</h3>
原告：{plaintiff_name}，{plaintiff_sex}，{plaintiff_ethnic}，{plaintiff_cellphone}，{plaintiff_birth}，{plaintiff_ID_number}，{plaintiff_address}。{plaintiff_company_name}，{plaintiff_company_address}，{plaintiff_company_legal_representative}。
委托代理人1：{plaintiff_attorney_name}，{plaintiff_attorney_sex}，{plaintiff_attorney_ethnic}，{plaintiff_attorney_birth}，{plaintiff_attorney_ID_number}，{plaintiff_attorney_address}。{plaintiff_lawyer_name}，{plaintiff_lawyer_office}，{plaintiff_lawyer_address}，{plaintiff_lawyer_telephone_number}。 
被告：{defendant_name}，{defendant_sex}，{defendant_ethnic}，{defendant_cellphone}，{defendant_birth}，{defendant_ID_number}，{defendant_address}。{defendant_company_name}，{defendant_company_address}，{defendant_company_legal_representative}。
委托代理人2：{defendant_attorney_name}，{defendant_attorney_sex}，{defendant_attorney_ethnic}，{defendant_attorney_birth}，{defendant_attorney_ID_number}，{defendant_attorney_address}。{defendant_lawyer_name}，{defendant_lawyer_office}，{defendant_lawyer_address}，{defendant_lawyer_telephone}。
诉讼请求：
{claims}
事实和理由：
　　{facts_and_reason1}

　　此致
{court_name}
　　　　　　　　　　　　　　　　　　　　　　　　　　<div style="text-align: right;">具状人：{plaintiff_name}</div>
　　　　　　　　　　　　　　　　　　　　　　　<div style="text-align: right;">日期：{date}</div>"""

                re_case_info_data = {}
                now_time = datetime.datetime.now().strftime('%Y年%m月%d日')
                for key in key_str.split(','):
                    if json_str.get(key, '') != '':
                        re_case_info_data[key] = json_str.get(key)
                    else:
                        re_case_info_data[key] = 'uu'
                re_case_info_data['date'] = now_time
                re_case_info_data['facts_and_reason'] = json_str.get('facts_and_reason') if json_str.get(
                    'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
                re_case_info_data['court_name'] = json_str.get('court_name') if json_str.get('court_name',
                                                                                             '') != '' else '_____人民法院'
                re_case_info_data['claims'] = claims_str
                str_data = json_str.get('facts_and_reason') if json_str.get(
                    'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
                lhqx = ''
                for choice_q in choices:
                    if choice_q['qid'] == "5c18c335ba92931aa9cb094c":
                        lh_choice_tags = choice_q.get("choice_tags", [])
                        for ii in lh_choice_tags:
                            lhqx = lhqx + ii.get('zh_name', '') + '、'
                        lhqx = lhqx[:len(lhqx) - 1]
                re_case_info_data[
                    'facts_and_reason1'] = "原被告双方于（    年   月，   方式相识），（    年  月  日办理结婚登记），子女于（    年  月  日   出生/无子女则不填写），由于婚后" + lhqx + \
                                           "。双方感情基础薄弱，婚后没注重夫妻感情的培养，缺乏良好的沟通，导致感情日益疏远，无法继续共同生活下去。"+ '\n\t'+str_data+'\n\t'+"为维护原告的合法权益，根据《中华人民共和国婚姻法》《中华人民共和国民事诉讼法》特向贵院起诉离婚，请求法院支持原告的诉讼请求。"

                re_str = text_lh.format(**re_case_info_data)
            elif subject_id == '5c175f52ba929379dd40fe81':  # 劳动双倍工资
                claims_str = ''
                jj = 1
                try:
                    # answer_ = requests.get('http://180.96.11.73:8122/api/znys/choice_record?record_id=%s' % (qid))
                    answer_ = requests.get('http://lmfy.assess.aegis-info.com/intelligentpretrial/znys/choice_record?record_id=%s' % (qid))
                    choices = json.loads(answer_.text).get('data', {}).get('temp_tags', [])

                except Exception as err:
                    print(err)
                    pass

                if True:
                    claims_str = claims_str + '　　' + str(jj) + '、' + '请求支付双倍工资' + str(
                        labor.get('money', '0')) + '元；\n'
                    jj = jj + 1
                suqiu = json_str.get('claims', [])
                for item in suqiu:
                    claims_str = claims_str + '　　' + str(jj) + '、' + item + '；\n'
                    jj = jj + 1
                claims_str = claims_str + '　　' + str(jj) + '、请求被告承担诉讼费。\n'

                key_str = "plaintiff_name,plaintiff_sex,plaintiff_ethnic,plaintiff_birth,plaintiff_ID_number,plaintiff_address,plaintiff_cellphone," \
                          "plaintiff_company_name,plaintiff_company_address,plaintiff_company_legal_representative,plaintiff_attorney_name,plaintiff_attorney_sex," \
                          "plaintiff_attorney_ethnic,plaintiff_attorney_ID_number,plaintiff_attorney_birth,plaintiff_attorney_address," \
                          "plaintiff_lawyer_name,plaintiff_lawyer_address,plaintiff_lawyer_office,plaintiff_lawyer_telephone_number," \
                          "defendant_name,defendant_sex,defendant_ethnic,defendant_birth,defendant_ID_number,defendant_address," \
                          "defendant_company_name,defendant_company_address,defendant_company_legal_representative," \
                          "defendant_attorney_name,defendant_attorney_sex,defendant_attorney_ethnic,defendant_attorney_birth," \
                          "defendant_telephone,defendant_attorney_ID_number,defendant_attorney_address,defendant_cellphone," \
                          "defendant_lawyer_name,defendant_lawyer_office,defendant_lawyer_address,defendant_lawyer_telephone," \
                          "claims,facts_and_reason,court_name,date"
                text_ld = """<h3 style="text-align: center;">民事起诉状</h3>
原告：{plaintiff_name}，{plaintiff_sex}，{plaintiff_ethnic}，{plaintiff_cellphone}，{plaintiff_birth}，{plaintiff_ID_number}，{plaintiff_address}。{plaintiff_company_name}，{plaintiff_company_address}，{plaintiff_company_legal_representative}。
委托代理人1：{plaintiff_attorney_name}，{plaintiff_attorney_sex}，{plaintiff_attorney_ethnic}，{plaintiff_attorney_birth}，{plaintiff_attorney_ID_number}，{plaintiff_attorney_address}。{plaintiff_lawyer_name}，{plaintiff_lawyer_office}，{plaintiff_lawyer_address}，{plaintiff_lawyer_telephone_number}。 
被告：{defendant_name}，{defendant_sex}，{defendant_ethnic}，{defendant_cellphone}，{defendant_birth}，{defendant_ID_number}，{defendant_address}。{defendant_company_name}，{defendant_company_address}，{defendant_company_legal_representative}。
委托代理人2：{defendant_attorney_name}，{defendant_attorney_sex}，{defendant_attorney_ethnic}，{defendant_attorney_birth}，{defendant_attorney_ID_number}，{defendant_attorney_address}。{defendant_lawyer_name}，{defendant_lawyer_office}，{defendant_lawyer_address}，{defendant_lawyer_telephone}。
诉讼请求：
{claims}
事实和理由：
　　原告自{start}至{end}在被告单位工作，每月工资{salary}元。在法律规定的应当签订劳动合同期间，未与原告签订书面劳动合同。签订书面劳动合同是单位的法定义务，被告的行为违反了《中华人民共和国劳动合同法》第10条的规定。因此原告基于《中华人民共和国劳动合同法》第八十二条的规定主张单位支付双倍工资{money}元。
　　{facts_and_reason}
    """+"\t"+"""原告已申请过劳动仲裁，但是对结果不服。
　　为了维护原告的合法权益，特向贵院起诉，愿判如所请。

　　此致
{court_name}
　　　　　　　　　　　　　　　　　　　　　　　　　　<div style="text-align: right;">具状人：{plaintiff_name}</div>
　　　　　　　　　　　　　　　　　　　　　　　<div  style="text-align: right;">日期：{date}</div>"""

                re_case_info_data = {}
                now_time = datetime.datetime.now().strftime('%Y年%m月%d日')
                for key in key_str.split(','):
                    if json_str.get(key, '') != '':
                        re_case_info_data[key] = json_str.get(key)
                    else:
                        re_case_info_data[key] = 'uu'
                re_case_info_data['date'] = now_time
                re_case_info_data['court_name'] = json_str.get('court_name') if json_str.get('court_name',
                                                                                             '') != '' else '______法院'
                re_case_info_data['facts_and_reason'] = json_str.get('facts_and_reason') if json_str.get(
                    'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
                re_case_info_data['claims'] = claims_str
                re_case_info_data['start'] = labor.get('start', '')
                re_case_info_data['end'] = labor.get('end', '')
                re_case_info_data['salary'] = labor.get('salary', '0')
                re_case_info_data['money'] = labor.get('money', '')
                re_str = text_ld.format(**re_case_info_data)
            aa = re_str.replace('uu，', '').replace('uu。', '').replace('uu', '')
            loc1 = aa.find('委托代理人1')
            loc2 = aa.find('被告')
            if json_str.get('plaintiff_attorney_name', '') == '' and json_str.get('plaintiff_lawyer_name', '') == '':
                aa = aa[:loc1] + aa[loc2:]
            loc3 = aa.find('委托代理人2')
            loc4 = aa.find('诉讼请求')
            if json_str.get('defendant_attorney_name', '') == '' and json_str.get('defendant_lawyer_name', '') == '':
                aa = aa[:loc3] + aa[loc4:]
            aa = aa.replace('委托代理人2', '委托代理人').replace('委托代理人1', '委托代理人')
            return aa

        claims_str = ''
        jj = 1
        try:
            answer_ = requests.get('http://lmfy.assess.aegis-info.com/intelligentpretrial/znys/choice_record?record_id=%s' % (qid))
            choices = json.loads(answer_.text).get('data', {}).get('temp_tags', [])
            if len(choices) > 0:
                choices_0 = choices[0].get('choice_tags', [])
                for ii in choices_0:
                    zh_name = ''#ii.get('zh_name', '')
                    if zh_name != '':
                        claims_str = claims_str + '　　' + str(jj) + '、' + zh_name + '；\n'
                        jj = jj + 1
        except Exception as err:
            print(err)
        suqiu  = json_str.get('claims', [])
        for item in suqiu:
            claims_str =claims_str + '　　' + str(jj) + '、' + item + '；\n'
            jj = jj + 1
        claims_str = claims_str + '　　' + str(jj) + '、请求被告承担诉讼费。\n'

        key_str = "plaintiff_name,plaintiff_sex,plaintiff_ethnic,plaintiff_birth,plaintiff_ID_number,plaintiff_address,plaintiff_cellphone," \
                  "plaintiff_company_name,plaintiff_company_address,plaintiff_company_legal_representative,plaintiff_attorney_name,plaintiff_attorney_sex," \
                  "plaintiff_attorney_ethnic,plaintiff_attorney_ID_number,plaintiff_attorney_birth,plaintiff_attorney_address," \
                  "plaintiff_lawyer_name,plaintiff_lawyer_address,plaintiff_lawyer_office,plaintiff_lawyer_telephone_number," \
                  "defendant_name,defendant_sex,defendant_ethnic,defendant_birth,defendant_ID_number,defendant_address," \
                  "defendant_company_name,defendant_company_address,defendant_company_legal_representative," \
                  "defendant_attorney_name,defendant_attorney_sex,defendant_attorney_ethnic,defendant_attorney_birth," \
                  "defendant_telephone,defendant_attorney_ID_number,defendant_attorney_address,defendant_cellphone," \
                  "defendant_lawyer_name,defendant_lawyer_office,defendant_lawyer_address,defendant_lawyer_telephone," \
                  "claims,facts_and_reason,court_name,date"
        text_ld = """<h3 style="text-align: center;">民事起诉状</h3>
原告：{plaintiff_name}，{plaintiff_sex}，{plaintiff_ethnic}，{plaintiff_cellphone}，{plaintiff_birth}，{plaintiff_ID_number}，{plaintiff_address}。{plaintiff_company_name}，{plaintiff_company_address}，{plaintiff_company_legal_representative}。
委托代理人1：{plaintiff_attorney_name}，{plaintiff_attorney_sex}，{plaintiff_attorney_ethnic}，{plaintiff_attorney_birth}，{plaintiff_attorney_ID_number}，{plaintiff_attorney_address}。{plaintiff_lawyer_name}，{plaintiff_lawyer_office}，{plaintiff_lawyer_address}，{plaintiff_lawyer_telephone_number}。 
被告：{defendant_name}，{defendant_sex}，{defendant_ethnic}，{defendant_cellphone}，{defendant_birth}，{defendant_ID_number}，{defendant_address}。{defendant_company_name}，{defendant_company_address}，{defendant_company_legal_representative}。
委托代理人2：{defendant_attorney_name}，{defendant_attorney_sex}，{defendant_attorney_ethnic}，{defendant_attorney_birth}，{defendant_attorney_ID_number}，{defendant_attorney_address}。{defendant_lawyer_name}，{defendant_lawyer_office}，{defendant_lawyer_address}，{defendant_lawyer_telephone}。
诉讼请求：
{claims}
事实和理由：
　　{facts_and_reason}

　　此致
{court_name}
　　　　　　　　　　　　　　　　　　　　　　　　　　<div style="text-align: right;">具状人：{plaintiff_name}</div>
　　　　　　　　　　　　　　　　　　　　　　　<div style="text-align: right;">日期：{date}</div>"""

        re_case_info_data = {}
        now_time = datetime.datetime.now().strftime('%Y年%m月%d日')
        for key in key_str.split(','):
            if json_str.get(key, '') != '':
                re_case_info_data[key] = json_str.get(key)
            else:
                re_case_info_data[key] = 'uu'
        re_case_info_data['date'] = now_time
        re_case_info_data['court_name'] = json_str.get('court_name') \
            if json_str.get('court_name', '') != '' else '_____人民法院'
        re_case_info_data['claims'] = claims_str

        if subject_id == '5c18475bba92937fab837eff':  # 房屋租赁合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            choice_tags_flag = 0  # 出租人
            if len(choices) > 1 and choices[0].get("choice_tags", [])[0].get('id') == '5c18486eba92937fb0af797b':
                choice_tags_flag = 1  # 承租人
            if choice_tags_flag == 0:
                json_str['facts_and_reason'] = """    年  月  日，原被告签订《房屋租赁合同》，约定被告承租原告所有的位于 小区房屋，建筑面积   平方米（房产证号     ），租赁期共   个月，自   年  月  日起至    年  月  日止。月租金    元，租金共计   元整。甲方向乙方收取房屋保证金     元。合同约定，租赁期间，乙方有以下行为之一的，甲方有权解除合同收回房屋：（1）未经甲方同意转租，转借，拆改变动房屋结构；（2）利用承租房屋存放危险物品或进行非法活动；（3）预期缴纳按约定应当由乙方交纳的各类费用；（4）下期房屋租金未提前一个月支付。在原告依约将房屋租赁给被告后，被告却屡次违反合同约定，拖欠房屋租金，原告多次索要无果。
　　原告依照双方签订的《房屋租赁合同》第  条之约定，行使单方解约权，告知被告   天后将收回该房产。但被告在接到通知   天后，拒不搬出。时至今日，仍拒不将房产交还原告。"""+ '\n\t'+str_data+'\n\t'+"""综上所述，被告的行为已严重侵犯了原告的合法权益。原告现依据《民事诉讼法》之相关规定向贵院提起诉讼，请求贵院依法支持原告的诉讼请求。"""
            else:
                json_str['facts_and_reason'] = """    年  月  日，原被告签订《房屋租赁合同》，约定原告承租被告所有的位于 小区房屋，建筑面积    平方米（房产证号     ），租赁期共   个月，自  年  月  日起至  年  月  日止。月租金   元，租金共计   元整。甲方（即被告）向乙方（即原告）收取房屋保证金    元。合同约定，甲方于   年  月  日向乙方交付房屋。合同签订后，被告一直未将房屋交付与原告，原告多次要求交房无果。"""+ '\n\t'+str_data+ '\n\t'+"""综上所述，被告的行为已严重侵犯了原告的合法权益。原告现依据《民事诉讼法》之相关规定向贵院提起诉讼，请求贵院依法支持原告的诉讼请求。"""
        elif subject_id == '5c185ec5ba92937fab837fb8':  # 担保合同纠纷 保证合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = """原被告于   年  月  日签订《保证合同》。合同约定在  情况下，由保证人替债务人向债权人偿还借款，之后再由债务人偿还保证人相应金额，原告认为，《保证合同》系合法有效的合同，对当事人具有法律约束力。当事人应当按照约定履行自己的义务，不得擅自变更或者解除合同。因此，在保证人    已经向债权人承担了自己的保证责任后，债务人应按照合同约定弥补保证人为此损失的金额，并且支付相应的迟延利息。
　　在此项借款中，共有  名担保人，按照担保合同约定，几位担保人就该项借款承担相应的责任，在我方已替债务人全部履行完还款义务后的前提下，有权请求其他的担保人承担相应的还款义务，向我方偿还相应金额。"""+ '\n\t'+str_data+'\n\t'+"""特向贵院起诉，请贵院依法维护原告的合法权益。"""
        elif subject_id == '5c177198ba92937fab837e4b':  # 保险合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = """    年  月  日，   在被告处投保了   险，保险期间为    年  月  日至    年  月  日。   年  月  日，发生      (简单描述保险事故过程），保险事故发生在保险期间内。因向被告保险公司索赔时未果，为维护原告的合法权益，特诉至法院。
　　原告认为，保险合同系合同双方基于自愿平等的前提签订，原告方在保险期间内发生保险事故，被告应当依约履行，被告的拒不赔付的行为显然构成对原告的违约。"""+ '\n\t'+str_data+'\n\t'+"""据此，原告为维护自身合法权益，依法提起诉讼，恳请法院判如所请，保护原告的合法权益。"""
        elif subject_id == '5c1748d4ba929311d9b45a05': # 变更抚养关系纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            qx = ''
            yc_choice_tags = choices[-1].get("choice_tags", [])
            for ii in yc_choice_tags:
                qx = qx + ii.get('colloquial_description', '') + '、'
            qx = qx[:len(qx) - 1]
            if qx =="没有上述情形":
                json_str['facts_and_reason']="原被告在    年  月  日登记结婚，婚后生育     。后双方因感情不和，原被告双方于    年  月  日离婚，并办理了离婚手续。离婚协议书约定（或判决书判决）  由（原告或被告）抚养。"+ '\n\t'+str_data+ '\n\t'+"综上所述，原告认为，（原告或被告）无法继续履行抚养子女的义务，现原告根据《中华人民共和国民事诉讼法》第一百零八条、《最高人民法院关于人民法院审理离婚案件处理子女抚养问题的若干具体意见的规定》16条的相关规定，诉至贵院，望贵院判决    由（原告或被告）抚养。"
            else:
                json_str['facts_and_reason'] ="原被告在    年  月  日登记结婚，婚后生育     。后双方因感情不和，原被告双方于    年  月  日离婚，并办理了离婚手续。离婚协议书约定（或判决书判决）  由（原告或被告）抚养。由（原告或被告）抚养期间，（原告或被告）"+ qx +"。"+ '\n\t'+str_data+ '\n\t'+"综上所述，原告认为，（原告或被告）无法继续履行抚养子女的义务，现原告根据《中华人民共和国民事诉讼法》第一百零八条、《最高人民法院关于人民法院审理离婚案件处理子女抚养问题的若干具体意见的规定》16条的相关规定，诉至贵院，望贵院判决  由（原告或被告）抚养。"
        elif subject_id == '5c135520ba929311d45d6d71':  # 机动车交通事故责任纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = """    年  月  日  时（事故发生时间） ，在     路（事故发生地点），原告与被告驾驶的车辆发生碰撞，致使原告        （按实际造成的损失填写）。后经    (交通事故发生地区/县)公安分局交巡警支队认定，被告对上述事故承担     责任，原告    责任（根据交警对交通事故如何认定实际填写）。（若构成伤残则出现以下内容）原告于    年  月  日，经   市道路交通事故鉴定中心伤残评定，确认 “    ，属  级伤残” ，但是双方就赔偿事宜未能达成一致意见。"""+ '\n\t'+str_data+ '\n\t'+"""原告认为，被告的行为显然构成对原告的侵权，并直接给原告造成了人身损害和经济损失，据此，原告为维护自身合法权益，依法提起诉讼，恳请法院判如所请，保护原告的合法权益。"""
        elif subject_id == '5c18a31dba92931aa72cffcb':  # 建设工程施工合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str[
                'facts_and_reason'] = """原告与被告于    年  月  日签订了建设工程合同，按照合同约定，原告为被告建设的位于   市   区   镇   地的   项目   楼的   工程进行施工，工期为   天，项目最后的结算金额为   元。合同还约定XXX的保证金/违约金条款（如有保证金或违约金条款填写）。"""+str_data+"""现被告   行为严重损害了原告的合法权益，故依《中华人民共和国民事诉讼法》的有关规定，特向贵院提起诉讼，请求依法裁判。"""
        elif subject_id == '5c18a400ba92931aac81b25d':  # 金融借款合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = """被告从    年  月  日到    年  月  日期间以  为由，分别  次向原告贷款人民币共  元，并约定于    年  月  日前还清，贷款利率为  利率，还款方式按    还本付息，逾期罚息按照合同约定上浮  计收。后被告逾期没有还清借款，经原告一直多次催讨，被告于    年  月  日还息  元后一直至今拒不清还，"""+str_data+"""故原告向法庭提起诉讼，要求被告返还贷款本金及利息  元并由被告承担本案诉讼费。
　　综上所述，为维护原告的合法权益，特向贵院提起诉讼，诉请如上。"""
        elif subject_id == '5c18a4e6ba92931aa9cb08ec':  # 买卖合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            choice_tags_flag = 0  # 卖方#######
            if len(choices) > 1 and choices[1].get("choice_tags", [])[0].get(
                    'id') == '5c19db71ba92937015bc05c':
                choice_tags_flag = 1  # 买方
            if choice_tags_flag == 0:
                qk1 = ''
                if len(choices) > 2:
                    yc_choice_tags_qk = choices[2].get("choice_tags", [])
                    if yc_choice_tags_qk[0].get('id') != '5c16f9b7ba929311d9b4594a':
                        for ii in yc_choice_tags_qk:
                            qk1 = qk1 + ii.get('zh_name', '') + '、'
                        qk1 = qk1[:len(qk1) - 1]
                tmp_qk1 = ''
                if qk1 != '':
                    tmp_qk1 = "但被告存在" + qk1 + "行为。"
                json_str[
                    'facts_and_reason'] = "    年  月  日，原告与被告签订一份《产品购销合同》，合同约定原告为被告供应   ，货物总价款为   元。双方约定了交货地点、验货及付款时间，逾期付款违约金等。合同签订后，原告依约于当日将货物发出，并由被告签收。" + \
                                          tmp_qk1 +'\n\t'+str_data+'\n\t'+"原告认为，依法成立的合同，对当事人具有法律约束力。当事人应当按照约定履行自己的合同义务。被告未能履行合同约定的义务，严重违反了合同约定。据此，原告为维护自身合法权益，依法提起诉讼，恳请法院判如所请，保护原告的合法权益。"
            else:
                qk = ''
                if len(choices) > 2:
                    yc_choice_tags_qk = choices[2].get("choice_tags", [])
                    if yc_choice_tags_qk[0].get('id') != '5c19e866ba92937015bc062a':
                        for ii in yc_choice_tags_qk:
                            qk = qk + ii.get('zh_name', '') + '、'
                        qk = qk[:len(qk) - 1]

                tmp_xw = ''
                if qk != '':
                    tmp_xw = "合同签订后，但被告存在" + qk + "行为。"

                json_str['facts_and_reason'] = "   年  月  日，原告与被告以签订一份《产品购销合同》，合同约定被告为原告供应   ，货物总价款为   元。" + \
                                               "双方约定了交货地点、验货及付款时间，逾期付款违约金等。" + tmp_xw + "经原告与其交涉无果。" + \
                                               '\n\t'+str_data+'\n\t'+"原告认为，依法成立的合同，对当事人具有法律约束力。当事人应当按照约定履行自己的合同义务。被告未能履行合同约定的义务，严重违反了合同约定。据此，原告为维护自身合法权益，依法提起诉讼，恳请法院判如所请，保护原告的合法权益。特向贵院起诉，请贵院依法维护原告的合法权益。"
        elif subject_id == '5c185a67ba92937fb0af7a42':  # 民间借贷纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = """    年  月  日被告向原告借款     元整。双方约定被告应于   年  月  日将借款还清给原告。合同签订后，原告即将借款交付给被告，但被告至今未清偿完毕。原告多次索要未果。"""+'\n\t'+str_data+'\n\t'+"""原告认为，依法成立的合同，对当事人具有法律约束力。当事人应当按照约定履行自己的义务。据此，根据双方《借款协议》约定和《中华人民共和国民事诉讼法》之相关规定，原告特向贵院提起诉讼，请求依法维护原告权利。
　　据此，根据双方《借款协议》约定和《中华人民共和国民事诉讼法》第二十五条的规定，原告特向贵院提起诉讼，请求依法维护原告权利。"""
        elif subject_id == '5c19ddfaba92937015bc05d3':  # 继承纠纷
            print(choices)
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            jcr = choices[0].get("choice_tags", [])[0].get('zh_name')
            yc = ''
            for choice_q in choices:
                if choice_q['qid'] == "5c1a05d7ba929370113bf72a":
                    yc_choice_tags1 = choice_q.get("choice_tags", [])
                    for ii in yc_choice_tags1:
                        yc = yc + ii.get('zh_name', '') + '、'
                    yc = yc[:len(yc) - 1]
                    print(yc)
            yz=""
            for choice_T in choices:
                if choice_T.get("choice_tags", [])[0].get(
                    'id') == '5c19f296ba929370113bf6e0':
                    yz = "，留有遗嘱"
                    break
                else:
                    yz=''
            yzfy=''
            for choice_Y in choices:
                if choice_Y.get("choice_tags", [])[0].get(
                    'id') == '5c19f50dba929370182557f3':
                    yzfy = ",留有遗赠抚养协议"
                    break
            else:
                yzfy=''
            json_str['facts_and_reason'] = "原告是逝者的" + jcr + "，逝者生前，原告对其尽了    义务，逝者去世后留有" + \
                                           yc + "遗产" + yz + yzfy + "，原告作为依法享有继承权的继承人有权继承逝者遗留下来的财产。但是     (若存在其它继承人因为遗产产生争议情形，请自行补充)。"+'\n\t'+str_data+'\n\t'+"为了维护原告的合法权益，特向贵院提起诉讼，愿判如所请。"
        elif subject_id == '5c1770c9ba92937fb0af78b3':  # 医疗损害赔偿纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            gs = ''
            if len(choices) > 2:
                yc_choice_tags = choices[2].get("choice_tags", [])
                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
            json_str[
                'facts_and_reason'] = "原告于    年  月  日因病住院，入院诊断为     ，于    年  月  日进行     手术，术后     (术后身体状况)，造成的损害是由于医院" + gs + \
                                      "。"+'\n\t'+str_data+'\n\t'+"原告方认为，根据《侵权责任法》第五十四条规定，患者在诊疗活动中受到损害，医疗机构及其医务人员有过错的，由医疗机构承担赔偿责任。被告的行为显然构成对原告的侵权，并且直接给原告方造成了人身损害和精神损失，据此，原告为维护自身合法权益，依法提起诉讼，恳请法院判如所请，保护原告的合法权益。"
        elif subject_id == '5c177d11ba92937fab837e8d':  # 农村土地承包合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str[
                'facts_and_reason'] = """原告和被告于    年  月  日签订了《土地承包合同》。合同约定     。原告认为，依法成立的合同，对当事人具有法律约束力。当事人应当按照约定履行自己的义务。但是被告        （填写被告存在的事实情形），未能履行合同约定的义务，严重违反了合同。现请求解除合同，被告承担违约金并承担本案所有诉讼费用。"""+'\n\t'+str_data+'\n\t'+"""为维护自身合法权益，特向贵院提起诉讼，恳请法院判如所请，保护原告的合法权益。"""
        elif subject_id == '5c16f983ba929311d0fbfc90':  # 分家析产纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str[
                'facts_and_reason'] = """原被告是   关系，一起共同生活多年，期间有家庭共同财产       ，但在共同生活期间，矛盾越来越多且无法调和，均认为不适合继续共同生活，但是对家庭共同财产分割的问题未能达成一致意见，协商多次未果，双方对财产分割各执一词。"""+'\n\t'+str_data+'\n\t'+"""为了公平合理的分割家庭共同财产，缓解家庭矛盾，故向贵院提起诉讼，恳请法院判如所请，保护原告的合法权益。"""
        elif subject_id == '5c107b61ba92931ebca385f6':#追索劳动报酬
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''

            json_str['facts_and_reason'] = """原告自    年  月  日到被告单位工作，从事   工作，每月工资   元，原告自入职后认真完成工作，但被告无故拖欠  个月的工资，经多次催讨后仍未支付。被告的行为违反了《中华人民共和国劳动合同法》第三十条以及《中华人民共和国劳动法》第五十条的规定。"""+'\n\t'+str_data+'\n\t'+"""多次协商后未能妥善解决问题，案件已经经过劳动仲裁，但对仲裁结果不服。
　　为了维护原告的合法权益，特向贵院提起诉讼，愿判如所请。"""
        elif subject_id == '5c18a671ba92931aac81b265':#物业服务合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''

            if len(choices) >3 and choices[0].get("choice_tags", [])[0].get(
                    'id') == '5c25cafcba929304cff14062':
                json_str['facts_and_reason'] = "被告系   市   街道  小区  幢  单元  室的住户。    年  月  日，  小区业主大会与原告订立物业服务合同，合同约定原告负责该小区的物业管理及服务，物业服务费按建筑面积每月每平方米  元，业主于每月 日前交纳。被告系该小区业主，其房屋建筑面积   平方米，每月应交   元。从    年  月  日起，被告就一直未缴纳物业费，原告一直催要未果。"+'\n\t'+str_data+'\n\t'+"原告认为，物业服务合同系合同双方基于自愿平等的前提签订，原告向被告履行约定的合同义务，被告理应按约定及时支付物业费。被告的行为侵犯了原告的合法权益。故此，原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"

            elif len(choices) >3 and choices[0].get("choice_tags", [])[0].get(
                    'id') == '5c19da3cba9293701825574b':
                gs = ''
                yc_choice_tags = choices[2].get("choice_tags", [])

                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
                json_str['facts_and_reason'] = "    年  月  日，原告购买了  市   街道  小区  幢  单元   室。    年  月  日，  小区业主大会与被告订立物业服务合同，合同约定被告负责该小区的物业管理及服务，物业服务费按建筑面积每月每平方米  元，业主于每月 日前交纳。在合同履行过程中，被告存在" + gs + "。"+'\n\t'+str_data+'\n\t'+"原告认为，物业服务合同系合同双方基于自愿平等的前提签订，原告向被告履行约定的合同义务，被告理应按约定提供物业服务。现被告未按约提供物业服务的行为侵犯了原告的合法权益。故此，原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
            else:
                pass
        elif subject_id == '5c177404ba92937fb0af78ce':#产品责任纠纷
            print(choices)
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            if len(choices) >4 and choices[-2].get("choice_tags", [])[0].get(
                    'id') == '5c1853cdba92937faf5da785':#销售者
                json_str['facts_and_reason'] = "原被告于    年  月  日签订买卖合同，合同约定由原告向被告购买   ，合同价款共计   元。合同签订后，原告支付了合同价款，被告向原告交付了   。然而，被告向原告交付的   存在产品缺陷，给原告造成了不可挽回的损失。"+'\n\t'+str_data+'\n\t'+"原告认为，因产品缺陷导致购买者人身或财产遭受损失的，销售者应当承担损害的赔偿责任。被告向原告交付的产品存在缺陷，导致原告遭受损失，被告的行为已构成侵权，严重侵犯了原告的合法权益。故而，现原告依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
            elif len(choices) >4 and choices[-2].get("choice_tags", [])[0].get(
                    'id') == '5c1852f9ba92937faf5da781':#
                json_str['facts_and_reason'] = "原告于    年  月  日购买被告生产的  ，然而，该产品存在严重的产品缺陷，给原告造成了不可挽回的损失。原告认为，因产品缺陷导致购买者人身或财产遭受损失的，生产者应当承担损害的赔偿责任。被告向原告交付的产品存在缺陷，导致原告遭受损失，被告的行为已构成侵权，严重侵犯了原告的合法权益。"+'\n\t'+str_data+'\n\t'+"故而，现原告依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c1861cbba92937fadd7450b':#相邻关系纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            gs = ''
            yc_choice_tags = choices[2].get("choice_tags", [])
            for ii in yc_choice_tags:
                gs = gs + ii.get('zh_name', '') + '、'
            gs = gs[:len(gs) - 1]
            json_str['facts_and_reason'] = "原告为  市  小区  室的业主，被告居住于该小区  室，原、被告之间是邻居关系,本应和睦相处。但是,被告存在"+ gs + "的行为，严重侵害的原告的权利,给原告造成了损失。"+'\n\t'+str_data+'\n\t'+"综上，原告认为被告的上述行为严重侵犯了原告的合法权益，且违反了相关法律法规的规定。原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c18995fba92931aa9cb088a':#承揽合同纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            if len(choices) >5 and choices[1].get("choice_tags", [])[0].get(
                    'id') == '5c189aeaba92931aac81b1f3':#定作人
                gs = ''
                yc_choice_tags = choices[-2].get("choice_tags", [])
                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
                json_str['facts_and_reason'] ="原被告于    年  月  日订立承揽合同，约定被告为原告定作一批   ，合同价款为   元。合同 签定后，原告将图纸等技术资料交付给被告，并向其预先支付价款   元，但被告一直存在"+ gs + "中的行为，致使原告不能按时使用，给原告造成了很大的损失。"+'\n\t'+str_data+'\n\t'+"原告认为，承揽合同系合同双方基于自愿平等的前提签订，原告已向被告履行约定的合同义务，被告理应按约定及时交付其工作成果。被告"+ gs + "的行为，侵犯了原告的合法权益。故此，原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
            elif len(choices) >5 and choices[1].get("choice_tags", [])[0].get(
                    'id') == '5c189b95ba92931aac81b1f5':#承揽人
                astr = ''
                yc_choice_tags = choices[-1].get("choice_tags", [])
                for ii in yc_choice_tags:
                    astr = astr + ii.get('zh_name', '') + '、'
                astr = astr[:len(astr) - 1]
                json_str['facts_and_reason'] = "原被告于    年  月  日订立承揽合同，约定原告为被告提供    的加工承揽服务，合同价款为   元。合同签订后，原告按照被告的需求向其交付了加工    。但是，被告在承揽合同履行过程中存在"+astr+"。"+'\n\t'+str_data+'\n\t'+"原告认为，承揽合同系合同双方基于自愿平等的前提签订，原告向被告履行约定的加工承揽义务，被告理应按约定履行义务。但其"+astr+"的行为，侵犯了原告的合法权益。故此，原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c1709e0ba929311d45d6e0b':#抚养费
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            if len(choices) >6 and choices[-2].get("choice_tags", [])[0].get(
                    'id') == '5c0f75faba92931ec02947c9':
                json_str['facts_and_reason'] = "原告  与被告原系夫妻关系，因感情破裂双方于    年  月  日办理了离婚。离婚时，双方约定原告随   生活，由被告每年承担抚养费    元，并于每年的  月  日支付当年的抚养费。但事后被告一直未能支付抚养费，  一个人抚养无法维持原告正常的学习和生活。原告多次要求被告支付抚养费均遭到拒绝。被告应向原告支付抚养费，其拒不履行支付抚养费义务的行为，不仅违反了法律规定，而且严重侵犯了原告的合法权益。"+'\n\t'+str_data+'\n\t'+"原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
            elif len(choices) >6 and choices[-2].get("choice_tags", [])[0].get(
                    'id') == '5c175dadba929311d45d6e98':
                json_str['facts_and_reason'] = "原告   与被告原系夫妻关系，因感情破裂双方于    年  月  日办理了离婚。离婚时，双方约定原告随   生活，由被告每年承担抚养费    元。然而，随着物价的上涨，约定的数额已远远低于当前的生活水平，原告多次与被告协商要求其增加抚养费均被拒绝。故原告起诉要求被告从    年  月  日起至其18周岁止每月承担抚养费   元。"+'\n\t'+str_data+'\n\t'+"原告依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c16f4bbba929311d45d6d8b':#赡养费纠纷
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] = "原告与被告系   关系，原告历尽艰辛、含辛茹苦将被告抚养成人，现原告年事已高，已丧失劳动能力，体弱多病，无生活来源，经常生病住院需要护理，生活困难，尤其是原告住院卧病在床期间，被告依然不管不问，原告多次要求被告支付赡养费均遭到拒绝。被告应对原告履行赡养义务，其拒不履行赡养义务的行为，不仅违反了法律规定，而且严重侵犯了原告的合法权益。"+'\n\t'+str_data+'\n\t'+"原告现依据《民事诉讼法》之相关规定，特起诉至贵院，恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c17725eba92937fb0af78b9':#扶养费
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            json_str['facts_and_reason'] ="原告与被告于    年  月  日登记结婚。   年  月  日原告因   疾病住院，入院之后，被告对原告不管不顾。" \
                                          "并且将原告的证件及夫妻共同财产控制在其手中，原告平时看病的费用与生活费被告也拒绝支付。" \
                                          " 现在原告的病情在不断加重，被告拒绝给原告支付医疗费，也不给支付生活费。" \
                                          +'\n\t'+str_data+'\n\t'+"被告应对原告履行扶养义务，其拒不履行扶养义务的行为，不仅违反了伤害了原告的感情，" \
                                          "而且严重侵犯了原告的合法权益。原告现依据《民事诉讼法》之相关规定，特起诉至贵院，" \
                                          "恳请贵院支持原告的诉讼请求，判如所请。"
        elif subject_id == '5c1c8da5ba92936be66ed395':#著作权纠纷
            print(choices)
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            if choices[0].get("choice_tags", [])[0].get(
                    'id') == '5c1c8dffba92936be66ed39b' and choices[4].get("choice_tags", [])[0].get(
                    'id') != '5c18882bba92931aac81b112':
                gs=""
                yc_choice_tags = choices[4].get("choice_tags", [])
                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
                json_str['facts_and_reason'] ="原告在    年（输入劳动合同签订年份）创作出作品《    》，并取得了作品的著作权利。" \
                                              "    年  月  日（输入日期），原告在   （输入地点、书籍、网站平台等）发现被告       （输入侵权行为）。" \
                                              +'\n\t'+str_data+'\n\t'+"被告未事先取得著作权人的许可，也未就使用行为支付相应报酬，" \
                                              "其使用行为侵犯了原告对该作品的"+gs+"。为维护著作权人的合法利益，特诉至法院。" \
                                              "原告认为，作品是是表达作者思想与观念的智力成果，对于作品著作权利的保护体现了社会对于知识与劳动的尊重。" \
                                              "因此，为维护著作权人的合法权益，依法提起诉讼，恳请法院依法裁判。"
            elif choices[0].get("choice_tags", [])[0].get(
                    'id') == '5c1c8e60ba92936be387f7d4' and choices[4].get("choice_tags", [])[0].get(
                    'id') != '5c18882bba92931aac81b112':
                gs = ""
                yc_choice_tags = choices[4].get("choice_tags", [])
                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
                json_str['facts_and_reason'] ="原告与权利人在    年（输入劳动合同签订年份）签订了《著作权授权合同》，并取得了作品《    》的著作权利。    年  月  日（输入日期），原告在   （输入地点、书籍、网站平台等）发现被告   （输入侵权行为）。"+'\n\t'+str_data+'\n\t'+"被告未事先取得著作权人的许可，也未就使用行为支付相应报酬，其使用行为侵犯了原告对该作品的"+gs+"。为维护著作权人的合法利益，特诉至法院。原告认为，作品是是表达作者思想与观念的智力成果，对于作品著作权利的保护体现了社会对于知识与劳动的尊重。因此，为维护著作权人的合法权益，依法提起诉讼，恳请法院依法裁判。"
            elif choices[0].get("choice_tags", [])[0].get(
                    'id') == '5c1c8ea7ba92936be387f7d7' and choices[4].get("choice_tags", [])[0].get(
                    'id') != '5c18882bba92931aac81b112':
                gs = ""
                yc_choice_tags = choices[4].get("choice_tags", [])
                for ii in yc_choice_tags:
                    gs = gs + ii.get('zh_name', '') + '、'
                gs = gs[:len(gs) - 1]
                json_str['facts_and_reason']="被继承人   （输入被继承人姓名），即原告的  （输入亲属关系）于    年死亡，被继承人生前享有合法著作权的作品《    》（输入作品名称）由原告依法继承并取得著作权。   年  月  日（输入日期），原告在   （输入地点、书籍、网站平台等）发现被告     （输入侵权行为）。"+'\n\t'+str_data+'\n\t'+"被告未事先取得著作权人的许可，也未就使用行为支付相应报酬，其使用行为侵犯了原告对该作品的"+gs+"。为维护著作权人的合法利益，特诉至法院。原告认为，作品是是表达作者思想与观念的智力成果，对于作品著作权利的保护体现了社会对于知识与劳动的尊重。因此，为维护著作权人的合法权益，依法提起诉讼，恳请法院依法裁判。"
            for dd in choices:
                if (dd.get("choice_tags")[0].get('id')  == '5c1c9ed2ba92936bea16864a') and (choices[choices.index(dd)+1].get("choice_tags", [])[0].get('id') == "5c18882bba92931aac81b112"):
                    gs = ""
                    yc_choice_tags = choices[-5].get("choice_tags", [])
                    for ii in yc_choice_tags:
                        gs = gs + ii.get('zh_name', '') + '、'
                    gs = gs[:len(gs) - 1]
                    json_str['facts_and_reason'] ="被告   （输入职工姓名）于    年  月  日至  于    年  月  日（输入工作期间）在原告   单位（输入原告单位名称）就职，且双方签订有《劳动合同》。被告基于原告所分配的工作任务，使用原告所提供的的物质技术条件创作了作品《    》（输入作品名称），故原告对该职务作品《    》享有著作权。    年  月  日，原告在  （输入地点、书籍、网站平台等）发现被告    （输入侵权行为）。"+'\n\t'+str_data+'\n\t'+"被告未事先取得著作权人的许可，也未就使用行为支付相应报酬，其使用行为侵犯了原告对该作品的  权和  权"+gs+"。为维护著作权人的合法利益，特诉至法院。原告认为，作品是是表达作者思想与观念的智力成果，对于作品著作权利的保护体现了社会对于知识与劳动的尊重。因此，为维护著作权人的合法权益，依法提起诉讼，恳请法院依法裁判。"
                else:
                    pass
        elif subject_id == "d2346bt008b864354cb08bfaa0a43c2v":
            text_ld="""<h3 style="text-align: center;">行政起诉状</h3>
原告：{plaintiff_name}，{plaintiff_sex}，{plaintiff_ethnic}，{plaintiff_cellphone}，{plaintiff_birth}，{plaintiff_ID_number}，{plaintiff_address}。{plaintiff_company_name}，{plaintiff_company_address}，{plaintiff_company_legal_representative}。
委托代理人1：{plaintiff_attorney_name}，{plaintiff_attorney_sex}，{plaintiff_attorney_ethnic}，{plaintiff_attorney_birth}，{plaintiff_attorney_ID_number}，{plaintiff_attorney_address}。{plaintiff_lawyer_name}，{plaintiff_lawyer_office}，{plaintiff_lawyer_address}，{plaintiff_lawyer_telephone_number}。 
被告：{defendant_name}，{defendant_sex}，{defendant_ethnic}，{defendant_cellphone}，{defendant_birth}，{defendant_ID_number}，{defendant_address}。{defendant_company_name}，{defendant_company_address}，{defendant_company_legal_representative}。
委托代理人2：{defendant_attorney_name}，{defendant_attorney_sex}，{defendant_attorney_ethnic}，{defendant_attorney_birth}，{defendant_attorney_ID_number}，{defendant_attorney_address}。{defendant_lawyer_name}，{defendant_lawyer_office}，{defendant_lawyer_address}，{defendant_lawyer_telephone}。
诉讼请求：
{claims}
事实和理由：
　　{facts_and_reason}

　　此致
{court_name}
　　　　　　　　　　　　　　　　　　　　　　　　　　具状人：{plaintiff_name}
　　　　　　　　　　　　　　　　　　　　　　　日期：{date}"""
            str_data = json_str.get('facts_and_reason') if json_str.get(
                'facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
            gs = ''
            yc_choice_tags = choices[-2].get("choice_tags", [])
            for ii in yc_choice_tags:
                gs = gs + ii.get('zh_name', '') + '、'
            gs = gs[:len(gs) - 1]
            if gs == "不存在上述情形":

                json_str['facts_and_reason']="    年  月  日，原告通过    政府信息公开平台向被告申请政府信息公开，要求公开       (填写所申请的政府信息)的相关材料。原告认为，被告没有按照原告要求公开政府信息的行政行为违法，严重侵害了原告的合法权益。原告为维护自己的权益，现依据《中华人民共和国政府信息公开条例》第三十三条第二款规定提起诉讼，请求法院依法维护原告的合法权益。"+ '\n\t'+str_data
            else:
                json_str['facts_and_reason'] ="    年  月  日，原告通过    政府信息公开平台向被告申请政府信息公开，要求公开       (填写所申请的政府信息)的相关材料。原告提交信息公开申请后，行政机关" + gs + "。" + "原告认为，被告没有按照原告要求公开政府信息的行政行为违法，严重侵害了原告的合法权益。原告为维护自己的权益，现依据《中华人民共和国政府信息公开条例》第三十三条第二款规定提起诉讼，请求法院依法维护原告的合法权益。"+ '\n\t'+str_data
        re_case_info_data['facts_and_reason'] = json_str.get('facts_and_reason') \
            if json_str.get('facts_and_reason', '') != '' and json_str.get('facts_and_reason', '') != '事实和理由' else ''
        re_str = text_ld.format(**re_case_info_data)
        aa = re_str.replace('uu，', '').replace('uu。', '').replace('uu', '')
        loc1 = aa.find('委托代理人1')
        loc2 = aa.find('被告')
        if json_str.get('plaintiff_attorney_name', '') == '' and json_str.get('plaintiff_lawyer_name', '') == '':
            aa = aa[:loc1] + aa[loc2:]
        loc3 = aa.find('委托代理人2')
        loc4 = aa.find('诉讼请求')
        if json_str.get('defendant_attorney_name', '') == '' and json_str.get('defendant_lawyer_name', '') == '':
            aa = aa[:loc3] + aa[loc4:]
        aa = aa.replace('委托代理人2', '委托代理人').replace('委托代理人1', '委托代理人')
        return aa


class ZNYS_Hot_Handler(handlers.NoAuthHandler):

    @decorator.handler_except
    def prepare(self):
        super(ZNYS_Hot_Handler, self).prepare()

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        result['data'] = {}
        result['data']['answer'] = self.get_znys_hot()
        return result

    def get_znys_hot(self):
        title_list = []
        answer = []
        try:
            query_params = {
                "query": {
                    "filtered": {
                        "filter": {
                            "range": {
                                "heat": {"gt": 5}
                            }
                        },
                        "query": {
                            "terms": {'caseCauseId': [9142, 9196, 9185, 9026, 9722, 9178, 9142, 9181, 9039, 9706]}
                        }
                    }
                }
            }
            result = es.search(index='law_question_v3', doc_type='questions', body={"query": query_params}, size=1000)
            for hit in result.get('hits').get('hits'):
                source = hit.get('_source')
                title = source.get('title', '')
                similarTitles = source.get('similarTitles', [])
                if title != '':
                    title_list.append(title)
                if similarTitles != []:
                    title_list += similarTitles
        except:
            pass
        if len(title_list) == 0:
            answer = ['我和公司没有签订劳动合同，能拿到赔偿吗？']
        elif len(title_list) <= 10:
            answer = title_list
        else:
            for ii in range(0, 10):
                answer.append(title_list[random.randint(0, len(title_list) - 1)])
        return answer


class DownloadLawComHandler(handlers.BaseHandler):
    """
@name 下载法律意见书
@description 下载法律意见书

@path
  /intelligentpretrial/android/law_push/DownloadLawComment:
    post:
      tags:
      - "下载法律意见书"

      produces:
      - "application/json"

      parameters:
      - name: "lawcomment"
        in: "body"
        description: "法律意见书"
        type: "string"
        required: true
      - name: "login"
        in: "query"
        description: "1为登录版本，0为非登录版本"
        required: false
      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/Qidown"
        504:
          description: "后台处理异常"
        404:
          description: "返回失败"

@endpath
@definitions
  Qidown:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/Path"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  Path:
    type: "object"
    properties:
      filepath:
        type: "string"
        description: "法律意见书文件路径"
@enddefinitions
    """
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(DownloadLawComHandler, self).prepare()
        self.lawcoment = self.get_argument("lawcomment", '')
        self.login = self.get_argument("login", 0)

    @decorator.threadpoll_executor
    def post(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        filedir = os.path.join(settings.get_static_absolute_path(), 'lawcomment')
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        now = str(time.time())
        filepath = os.path.join(filedir, '法律意见书_{}.html'.format(now))
        with open(filepath, 'wb') as f:
            f.write(self.lawcoment.encode('utf-8'))

        outputfile = filepath.replace('html', 'docx')
        try:
            output = pypandoc.convert_file(filepath, 'docx', outputfile=outputfile)
        except Exception as err:
            print(err.args)
        result['data'] = {}
        if int(self.login) == 0:
            domain ='http://noauth.aegis-info.com'
        else:
            domain = 'http://intelligentpretrial.aegis-info.com'
        result['data']['filepath'] = domain+'/static/lawcomment/{}'.format(os.path.basename(outputfile))
        return result


class EmailLawComHandler(handlers.BaseHandler):

    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(EmailLawComHandler, self).prepare()
        self.lawcoment = self.get_argument("lawcomment", '')
        self.to_mail = self.get_argument("to_mail", "")

    @decorator.threadpoll_executor
    def post(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        filedir = os.path.join(settings.get_static_absolute_path(), 'lawcomment/email')
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        now = str(time.time())
        # filepath = os.path.join(filedir, crypto.md5('法律意见书_{}'.format(now))+'.html')
        filepath = os.path.join(filedir, '法律意见书.html')
        with open(filepath, 'wb') as f:
            f.write(self.lawcoment.encode('utf-8'))

        self.outputfile = filepath.replace('html', 'docx')
        try:
            output = pypandoc.convert_file(filepath, 'docx', outputfile=self.outputfile)
        except Exception as err:
            print(err.args)
        send_email(self.to_mail, '法律意见书', attachment=self.outputfile)
        result['data'] = {}
        return result

    @decorator.handler_except
    def on_finish(self):
        os.remove(self.outputfile)


class DownloadIndictmentHandler(handlers.BaseHandler):
    """
@name 下载起诉状
@description 下载起诉状
@path
  /intelligentpretrial/android/law_push/DownloadIndictment:
    post:
      tags:
      - "下载起诉状"

      parameters:
      - name: "indictment"
        in: "query"
        description: "起诉状"
        required: true
      - name: "login"
        in: "query"
        description: "1为登录版本，0为非登录版本"
        required: false

      responses:
        200:
          description: "发送成功"
          schema:
            $ref: "#/definitions/Qisudown"
        400:
          description: "返回失败"
@endpath
@definitions
  Qisudown:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/QisuPath"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  QisuPath:
    type: "object"
    properties:
      filepath:
        type: "string"
        description: "起诉状文件路径"
@enddefinitions
    """

    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(DownloadIndictmentHandler, self).prepare()
        self.indictment = self.get_argument('indictment', '')
        self.login = self.get_argument("login", 0)

    @decorator.threadpoll_executor
    def post(self, *args, **kwargs):
        """IO操作"""

        result = self.init_response_data()
        filedir = os.path.join(settings.get_static_absolute_path(), 'indictment')
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        now = str(time.time())
        filepath = os.path.join(filedir, '起诉状_{}.html'.format(now))
        with open(filepath, 'wb') as f:
            f.write(self.indictment.encode('utf-8'))

        outputfile = filepath.replace('html', 'docx')
        try:
            output = pypandoc.convert_file(filepath, 'docx', outputfile=outputfile)
        except Exception as err:
            print(err.args)

        result['data'] = {}
        if int(self.login) == 0:
            domain ='http://noauth.aegis-info.com'
        else:
            domain = 'http://intelligentpretrial.aegis-info.com'
        result['data']['filepath'] =domain+ '/static/indictment/{}'.format(os.path.basename(outputfile))

        return result


class EmailIndictmentHandler(handlers.BaseHandler):

    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(EmailIndictmentHandler, self).prepare()
        self.indictment = self.get_argument('indictment', '')
        self.to_mail = self.get_argument("to_mail", "")

    @decorator.threadpoll_executor
    def post(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        filedir = os.path.join(settings.get_static_absolute_path(), 'indictment/email')
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        now = str(time.time())
        filepath = os.path.join(filedir, crypto.md5('起诉状_{}'.format(now))+'.html')
        with open(filepath, 'wb') as f:
            f.write(self.indictment.encode('utf-8'))

        self.outputfile = filepath.replace('html', 'docx')
        try:
            output = pypandoc.convert_file(filepath, 'docx', outputfile=self.outputfile)
        except Exception as err:
            print(err.args)
        send_email(self.to_mail, '起诉状', attachment=self.outputfile)
        result['data'] = {}
        return result

    @decorator.handler_except
    def on_finish(self):
        os.remove(self.outputfile)


class LawOpinionHandler(handlers.BaseHandler):
    """
@name 行动建议
@description 行动建议

@path
  /intelligentpretrial/android/law_push/Law_Comment:
    get:
      tags:
      - "行动建议"

      produces:
      - "application/json"

      parameters:
      - name: "qid"
        in: "query"
        description: "选项记录的id"
        type: "string"
        required: true

      responses:
        200:
          description: "返回成功"
          schema:
            $ref: "#/definitions/Advice"
        504:
          description: "后台处理异常"
        404:
          description: "返回失败"

@endpath

@definitions
  Advice:
    type: "object"
    properties:
      data:
        $ref: "#/definitions/LawPush"
      msg:
        type: "string"
      code:
        type: "integer"
        description: "200返回成功，400返回失败"
        enum:
        - "200"
        - "400"
  LawPush:
    type: "object"
    properties:
      money:
        type: "integer"
        description: "赔偿金额"
      action_comment:
        type: "string"
        description: "行动建议内容"
@enddefinitions

    """
    @decorator.handler_except
    def prepare(self):
        """在请求方法 get、post等执行前调用，进行通用的参数初始化，支持协程"""
        super(LawOpinionHandler, self).prepare()
        self.start = self.get_argument("start", '1')
        self.end = self.get_argument("end", '1')
        self.salary = int(self.get_argument("salary", '0'))
        self.time_of_award = self.get_argument("time_of_award", '1') or '1'
        self.qid = self.get_argument("qid", '')

    @decorator.threadpoll_executor
    def get(self, *args, **kwargs):
        """IO操作"""
        result = self.init_response_data()
        result['data'] = {}
        answer = self.law_comment(self.start, self.end, self.salary, self.time_of_award, self.qid).get('data', {})
        if answer.get('support', 0.0) != 0.0:
            result['data']['support'] = answer.get('support', 0.0)
        result['data']['action_comment'] = answer.get('action_comment', '')
        result['data']['money'] = int(answer.get('money', 0))
        return result

    def law_comment(self, start, end, salary, time_of_award, qid):
        znysmodel = Choice_recordModel()
        znysarmodel = Topic_recommendModel()
        subject_id = znysmodel.get_subject_id(qid)
        result = {'data': {}}
        leap_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        no_leap_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if salary != 0:
            time_s = start.split('-')
            time_e = end.split('-')
            tmp_time_of_award = time_of_award
            if time_of_award == '1' or time_of_award == None:
                time_of_award = datetime.datetime.now().strftime("%Y-%m-%d")
            time_of_award = time_of_award.split('-')
            int_s = [int(ii) for ii in time_s]
            int_e = [int(ii) for ii in time_e]
            int_award = [int(ii) for ii in time_of_award]
            data_s = datetime.date(int_s[0], int_s[1], int_s[2])
            if (int_s[0] % 400 == 0) or (int_s[0] % 4 == 0 and int_s[0] % 100 != 0):
                delta_n = datetime.timedelta(days=leap_month[int_s[1] - 1])
            else:
                delta_n = datetime.timedelta(days=no_leap_month[int_s[1] - 1])
            data_s_30 = data_s + delta_n
            data_e = datetime.date(int_e[0], int_e[1], int_e[2])
            data_award = datetime.date(int_award[0], int_award[1], int_award[2])
            delta = datetime.timedelta(days=30)
            delta1 = datetime.timedelta(days=1)
            delta365 = datetime.timedelta(days=365)
            if (int_s[0] == int_e[0] and (
                    (int_s[1] + 1 == int_e[1] and int_s[2] < int_e[2]) or int_s[1] == int_e[1])) or \
                    (int_s[0] + 1 == int_e[0] and int_s[1] == 12 and int_e[1] == 1 and int_s[2] < int_e[2]):
                money = 0
                answer = "    你是" + time_s[0] + "年" + time_s[1] + "月" + time_s[2] + "日到单位工作，截止" + time_e[0] + "年" + \
                         time_e[1] + "月" + time_e[2] + "日你还未签劳动合同且在该单位工作不满一个月。" \
                                                       "按照《劳动合同法》第10条的规定，单位应当在你入职的一个月内与你签订劳动合同，所以单位未与你签劳动合同仍在合法期限内，" \
                                                       "而请求单位支付未签劳动合同的双倍工资是从工作满一个月的次日开始起算的，鉴于你工作不满一个月，所以无法请求单位支付未签订劳动合同的双倍工资。"
            elif int_s[0] == int_e[0] or (int_s[0] + 1 == int_e[0] and int_s[1] > int_e[1]) \
                    or (int_s[0] + 1 == int_e[0] and int_s[1] == int_e[1] and int_s[2] >= int_e[2]):
                month = int_e[1] - int_s[1]
                day = int_e[2] - int_s[2]
                if month > 0:
                    money = round(salary * (month - 1) + salary * day / 30, 2)
                else:
                    money = round(salary * (month + 11) + salary * day / 30, 2)
                data_ee = data_e + delta1
                data_eee = data_e + delta365
                answer = "    你是" + time_s[0] + "年" + time_s[1] + "月" + time_s[2] + "日到单位工作，截止" + time_e[0] + "年" + \
                         time_e[1] + "月" + time_e[2] + "日你还未签劳动合同且在该单位工作不满一年。 " \
                                                       "按照《劳动合同法》第10条的规定，单位应当在你入职的一个月内与你签订劳动合同。但你工作满一个月了，单位也未和你签劳动合同，因此单位已经超过了签订劳动合同的法定时间。" \
                                                       "所以你可以根据《劳动合同法实施条例》第6条向公司主张<b>" + str(
                    data_s_30.year) + "年" + str(data_s_30.month) + "月" + str(data_s_30.day) + "日至" + time_e[0] + "年" + \
                         time_e[1] + "月" + time_e[2] + "日</b>这段期间的双倍工资。\n" \
                                                       "    但是根据《劳动争议调解仲裁法》第27条的规定，你需要在权利受到侵害之日起1年内主张你的两倍工资才有可能得到支持。" \
                                                       "也就是说你需要在<b>" + str(data_eee.year) + "年" + str(
                    data_eee.month) + "月" + str(data_eee.day) + "日</b>之前向劳动仲裁委员会申请仲裁，一旦超过此时间段就难以得到支持。" \
                                                                "由于你在该单位工作不满一年，在1年有效仲裁时效期间内主张未签劳动合同两倍工资差额，则从工作满一个月之次日起到未签劳动合同之日期间主张两倍工资差额可以得到认可，" \
                                                                "即可主张" + str(data_s_30.year) + "年" + str(
                    data_s_30.month) + "月" + str(data_s_30.day) + "日至" + time_e[0] + "年" + time_e[1] + "月" + time_e[
                             2] + "日期间未签劳动合同的两倍工资差额。"
            elif (data_e - data_s).days >= 365 and (data_award - data_s).days <= 365 * 2:  # and int_s[2] <= int_e[2]
                data_award_365 = data_award - delta365
                data_award_3651 = data_award - delta365 - delta1
                data_s_365 = data_s + delta365 - delta1
                data_s_3651 = data_s + delta365
                data_s_3652 = data_s + delta365 + delta365

                if (data_award - data_s).days <= 365:
                    month = data_award.month - data_s.month
                    day = data_award.day - data_s.day
                    if month > 0:
                        money = round(salary * (month - 1) + salary * day / 30, 2)
                    else:
                        money = round(salary * (month + 11) + salary * day / 30, 2)
                else:
                    month = data_s_365.month - data_award.month
                    day = data_s_365.day - data_award.day
                    if month > 0:
                        money = round(salary * month + salary * day / 30, 2)
                    else:
                        money = round(salary * (month + 12) + salary * day / 30, 2)
                if tmp_time_of_award == '1' or tmp_time_of_award == None:
                    answer = "    你是" + time_s[0] + "年" + time_s[1] + "月" + time_s[2] + "日到单位工作，截止" + time_e[0] + \
                             "年" + time_e[1] + "月" + time_e[2] + "日你还未签劳动合同。由于未明确申请劳动仲裁时间，因此你" \
                                                                 "最迟需要在" + str(data_s_3652.year) + "年" + str(
                        data_s_3652.month) + "月" + str(data_s_3652.day) + \
                             "日前申请仲裁才有可能拿到部分的双倍工资。"
                else:
                    answer = "    你是" + time_s[0] + "年" + time_s[1] + "月" + time_s[2] + "日到单位工作，截止" + time_e[0] + "年" + \
                             time_e[1] + "月" + time_e[2] + "日你还未签劳动合同且在该单位工作已满一年。" \
                                                           "按照《劳动合同法》第10条的规定，单位应当在你入职的一个月内与你签订劳动合同。但你工作满一个月了，单位也未和你签劳动合同，因此单位已经超过了签订劳动合同的法定时间。" \
                                                           "所以你可以根据《劳动合同法实施条例》第7条向公司主张<b>" + str(
                        data_award_365.year) + "年" + str(data_award_365.month) + "月" + str(data_award_365.day) + \
                             "日至" + str(data_s_3651.year) + "年" + str(data_s_3651.month) + "月" + str(
                        data_s_3651.day) + "日</b>这段期间的双倍工资。" \
                                           "另外，自用工之日起满一年未签劳动合同，还视为单位自" + str(data_s_3651.year) + "年" + str(
                        data_s_3651.month) + "月" + str(data_s_3651.day) + "日起就与你订立了无固定期限劳动合同，" \
                                                                          "若在工作中没有重大违法违纪行为，而单位将你辞退，则可以要求单位支付经济赔偿金。\n    但是根据《劳动争议调解仲裁法》第27条的规定，你需要在权利受到侵害之日起1年内主张你的两倍工资才有可能得到支持。" \
                                                                          "也就是说你需要在<b>" + str(
                        data_s_3652.year) + "年" + str(data_s_3652.month) + "月" + str(data_s_3652.day) + \
                             "日</b>之前向劳动仲裁委员会申请仲裁，一旦超过此时间段就难以得到支持。由于你在" + str(data_award.year) + "年" + str(
                        data_award.month) + "月" + str(data_award.day) + "日提出仲裁申请，" \
                                                                        "则要求" + str(data_award_3651.year) + "年" + str(
                        data_award_3651.month) + "月" + str(data_award_3651.day) + "日前的未签订劳动合同的两倍工资差额，明显已超过申请仲裁时效期间，" \
                                                                                  "故对主张的" + str(
                        data_award_3651.year) + "年" + str(data_award_3651.month) + "月" + str(
                        data_award_3651.day) + "日前的两倍工资差额不予认可，" \
                                               "仅支持" + str(data_award_365.year) + "年" + str(
                        data_award_365.month) + "月" + str(data_award_365.day) + "日至" + str(
                        data_s_3651.year) + "年" + str(data_s_3651.month) + "月" + str(data_s_3651.day) + \
                             "日期间未签劳动合同的两倍工资差额。"
            else:
                money = 0
                answer = "    你是" + time_s[0] + "年" + time_s[1] + "月" + time_s[2] + "日到单位工作，截止" + time_e[0] + "年" + \
                         time_e[1] + "月" + time_e[2] + "日你还未签劳动合同。" \
                                                       "但是由于你超过了申请劳动仲裁的时效期间，你的请求将不受法律保护，所以你请求单位支付未签劳动合同双倍工资赔偿的主张不会得到支持。"

        recommandatoin_list =znysarmodel.find_one_by_query(query={"id":subject_id})
        # print(recommandatoin_list)
        recommandatoin = ''
        if recommandatoin_list:
            for ii in recommandatoin_list['recommended_actions']:
                recommandatoin = recommandatoin + ii + '\n'
        result["data"]['action_comment'] = recommandatoin
        return result



handlers = [
    (r"/intelligentpretrial/android/law_push/Law_Comment", LawOpinionHandler),
    (r"/intelligentpretrial/android/law_push/ZNYS_SSS_Handler", ZNYS_SSS_Handler),
    (r"/intelligentpretrial/android/law_push/ZNYS_Hot_Handler", ZNYS_Hot_Handler),
    (r"/intelligentpretrial/android/law_push/DownloadLawComment", DownloadLawComHandler),
    (r"/intelligentpretrial/android/law_push/EmailLawComHandler", EmailLawComHandler),
    (r"/intelligentpretrial/android/law_push/DownloadIndictment", DownloadIndictmentHandler),
    (r"/intelligentpretrial/android/law_push/EmailIndictmentHandler", EmailIndictmentHandler),
]
