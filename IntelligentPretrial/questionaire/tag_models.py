#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/8 13:34
# @Author  : Niyoufa


import json
import time
from enum import Enum
from pymongo import UpdateOne
from questionaire import utils
from questionaire.base_model import BaseMongo
from questionaire.maintain_model import maintain_handler
from microserver.utils import crypto
from microserver.utils.singleton import Singleton
from microserver.db.mongodb import MongoDB



# 标签类型枚举
class TagType(Enum):
    Tag = (0, "tag", "普通标签")

    Cause = (1, "cause", "案由")

    GraphCategory = (10, "graph_category", "图谱分类")

    LawCategory = (20, "law_category", "标签法律分类")

    ExtratctMethod = (30, "extract_method", "提取方法")

    Para = (40, "para", "段落")

    DocType = (41, "doc_type", "文书类型")

    Procedure = (42, "procedure", "适用程序")

    RuleType = (50, "rule", "规则类型")

    LawSystem = (60, "law_system", "法律体系")

    NewLawCategory = (70, "new_law_category", "新标签法律分类")

    Entity = (80, "entity", "实体")

    @classmethod
    def check_type(cls, type):
        values = [obj.value[0] for obj in list(cls.__members__.values())]

        if type not in values:
            raise Exception("标签类型错误！")

    @classmethod
    def tag_types(cls):
        return [obj.value for obj in list(cls.__members__.values())]


class NlpMongo(BaseMongo, Singleton):
    _alias_name = "mongodb"

    def __init__(self, name):
        self._name = name


# 标签
class TagModel(BaseMongo, Singleton):
    _name = "tag.tag"
    _alias_name = "mongodb"

    @maintain_handler
    def create(self, vals, *args, **kwargs):
        # 类型
        type = vals.get("type")
        if type:
            type = int(type)
            TagType.check_type(type)

        # 标签中文名
        zh_name = vals.get("zh_name")

        # 标签别名
        alias_name = vals.get("zh_name")

        # 标签描述
        description = vals.get("description")

        # 标签文案
        document = vals.get("document")

        # 口语化描述
        colloquial_description = vals.get("colloquial_description")

        # 标签关键词 以\n符分割的字符串
        keywords = vals.get("keywords") or ""

        # 全文关键词
        doc_keywords = vals.get("doc_keywords") or ""

        # 标签不包含关键词，字符串
        exclude_keywords = vals.get("exclude_keywords") or ""

        # 规则
        rules = vals.get("rules")
        self.check_rules(rules)

        # 解析提取方法
        extract_type = vals.get("extract_type")
        if extract_type and not self.get_count({"id": extract_type}):
            raise Exception("解析提取方法不存在！")

        # 解析内容
        extracts = vals.get("extracts")
        self.check_extracts(extracts)
        if extracts != None:
            temp_extracts = []
            for extract in extracts:
                graph_type = extract.get("graph_type")
                table = extract.get("table")
                name = extract.get("name")
                id = extract.get("id")
                rules = extract.get("rules") or []
                chain_rules = extract.get("chain_rules") or []
                temp_extracts.append(dict(
                    graph_type=graph_type,
                    table=table,
                    name=name,
                    id=id,
                    rules=rules,
                    chain_rules=chain_rules,
                ))
            extracts = temp_extracts

        # 树属性
        has_child = vals.get("has_child")
        if not isinstance(has_child, bool):
            has_child = None

        parent = vals.get("parent")
        if parent and not self.get_count({"id": parent, "type": type}):
            raise Exception("parent不存在！")

        top_parent = vals.get("top_parent")
        if top_parent and not self.get_count({"id": top_parent, "type": type}):
            raise Exception("top_parent不存在！")

        rel_id = vals.get("rel_id")

        # 段落标签
        doc_type = vals.get("doc_type")
        if doc_type:
            doc_type = int(doc_type)

        if doc_type and not self.get_count({"id": doc_type}):
            raise Exception("文档类型不存在！")

        program = vals.get("program")
        if program and not self.get_count({"id": program}):
            raise Exception("使用程序不存在！")

        # 标签id
        id = vals.get("id")
        if not id:
            if type == TagType.NewLawCategory.value[0]:
                id = crypto.md5(str(time.time()))
            else:
                if not zh_name:
                    raise Exception("zh_name参数不能为空！")
                else:
                    id = crypto.md5("%s%s" % (type, zh_name))

        # 关联旧标签id
        related_ids = vals.get("related_ids") or []

        obj = dict(
            id=id,
            type=type,
            zh_name=zh_name,
            alias_name=alias_name,
            description=description,
            document=document,
            colloquial_description=colloquial_description,
            keywords=keywords,
            doc_keywords=doc_keywords,
            exclude_keywords=exclude_keywords,
            rules=rules,
            extract_type=extract_type,
            extracts=extracts,
            has_child=has_child,
            parent=parent,
            top_parent=top_parent,
            rel_id=rel_id,
            doc_type=doc_type,
            program=program,
            related_ids=related_ids,
        )

        if type == TagType.NewLawCategory.value[0]:
            count_params = {"$or": [{"id": id, "type": type}, {"zh_name": zh_name, "type": type, "parent": parent}]}
        else:
            count_params = {"$or": [{"id": id, "type": type}, {"zh_name": zh_name, "type": type},
                                    {"alias_name": zh_name, "type": type}]}

        if self.get_count(count_params):
            raise Exception("已存在！")
        else:
            return super(TagModel, self).create(obj, count_params=count_params, **kwargs)

    @maintain_handler
    def update(self, vals, *args, **kwargs):
        # 查询参数
        query_params = kwargs.get("query_params")
        update_obj = self.search_read(query_params=query_params, detail=False)[0][0]
        id = update_obj.get("id")
        obj = {}

        # 类型
        type = kwargs.get("type")
        if type == None:
            raise Exception("type不能为空！")
        else:
            type = int(type)
            TagType.check_type(type)

        # 标签中文名不支持修改，实际修改的是标签别名
        zh_name = vals.get("zh_name")
        if zh_name:
            if self.get_count(query_params={"$or": [{"zh_name": zh_name}, {"alias_name": zh_name}], "id": {"$ne": id},
                                            "type": type}):
                raise Exception("标签：%s已存在" % zh_name)
            else:
                obj.update(dict(
                    alias_name=zh_name,
                ))

        # 标签描述
        description = vals.get("description")
        if description is not None:
            obj.update(dict(
                description=description,
            ))

        # 标签文案
        document = vals.get("document")
        if document is not None:
            obj.update(dict(
                document=document,
            ))

        # 口语化表示
        colloquial_description = vals.get("colloquial_description")
        if colloquial_description != None:
            obj.update(dict(
                colloquial_description=colloquial_description
            ))

        # 标签关键词
        keywords = vals.get("keywords")
        if keywords != None:
            obj.update(dict(
                keywords=keywords,
            ))

        # 全文关键词
        doc_keywords = vals.get("doc_keywords") or ""
        if doc_keywords != None:
            obj.update(dict(
                doc_keywords=doc_keywords,
            ))

        # 标签不包含关键词
        exclude_keywords = vals.get("exclude_keywords")
        if exclude_keywords != None:
            obj.update(dict(
                exclude_keywords=exclude_keywords
            ))

        # 拆分标签
        split_tags = vals.get("split_tags")
        self.check_split_tags(split_tags)
        if split_tags != None:
            obj.update(dict(
                split_tags=split_tags
            ))

        # 是否是常用标签
        is_common = vals.get("is_common")
        if is_common != None and is_common != "":
            obj.update(dict(
                is_common=is_common
            ))

        # 问题关键词
        question_keywords = vals.get("question_keywords")
        if question_keywords:
            if not isinstance(question_keywords, list):
                raise Exception("question_keywords参数类型错误！")
            question_keywords = list(set(question_keywords))
            obj.update(dict(
                question_keywords=question_keywords
            ))

        # 规则
        rules = vals.get("rules")
        self.check_rules(rules)
        if rules != None:
            obj.update(dict(
                rules=rules,
            ))

        # 解析提取方法
        extract_type = vals.get("extract_type")
        if extract_type and not self.get_count({"id": extract_type}):
            raise Exception("解析提取方法不存在！")
        if extract_type:
            obj.update(dict(
                extract_type=extract_type
            ))

        # 解析内容
        extracts = vals.get("extracts")
        self.check_extracts(extracts)
        if extracts != None:
            temp_extracts = []
            for extract in extracts:
                graph_type = extract.get("graph_type")
                table = extract.get("table")
                name = extract.get("name")
                id = extract.get("id")
                rules = extract.get("rules") or []
                chain_rules = extract.get("chain_rules") or []
                temp_extracts.append(dict(
                    graph_type=graph_type,
                    table=table,
                    name=name,
                    id=id,
                    rules=rules,
                    chain_rules=chain_rules,
                ))
            extracts = temp_extracts
            obj.update(dict(
                extracts=extracts
            ))

        # 树属性
        has_child = vals.get("has_child")
        if isinstance(has_child, bool):
            obj.update(dict(
                has_child=has_child
            ))

        if "parent" in vals:
            parent = vals.get("parent")
            if parent and not self.get_count({"id": parent, "type": type}):
                raise Exception("parent不存在:%s！" % (obj.get("parent")))
            else:
                obj.update(dict(
                    parent=parent
                ))

        if "top_parent" in vals:
            top_parent = vals.get("top_parent")
            if top_parent and not self.get_count({"id": top_parent, "type": type}):
                raise Exception("top_parent不存在！")
            else:
                obj.update(dict(
                    top_parent=top_parent
                ))

        rel_id = vals.get("rel_id")
        if rel_id:
            obj.update(dict(
                rel_id=rel_id,
            ))

        # 段落标签
        doc_type = vals.get("doc_type")
        if doc_type:
            doc_type = int(doc_type)
        if doc_type and not self.get_count({"id": doc_type}):
            raise Exception("文档类型不存在！")
        if doc_type:
            obj.update(dict(
                doc_type=doc_type
            ))

        # 审理程序
        program = vals.get("program")
        if program and not self.get_count({"id": program}):
            raise Exception("使用程序不存在！")
        if program:
            obj.update(dict(
                program=program
            ))

        # 提取方法table
        table = vals.get("table")
        if table:
            obj.update(dict(
                table=table
            ))

        # 关联旧标签体系id
        related_ids = vals.get("related_ids")
        if related_ids and isinstance(related_ids, list):
            obj.update(dict(
                related_ids=related_ids
            ))

        super(TagModel, self).update(obj, **kwargs)

    def check_split_tags(self, split_tags):
        if split_tags:
            if not isinstance(split_tags, list):
                raise Exception("split_tags参数类型错误！")
            for tag in split_tags:
                if not self.get_count({"id": tag}):
                    raise Exception(tag + "标签不存在！")

    def check_rules(self, rules):
        if rules:
            if not isinstance(rules, list):
                raise Exception("rules参数类型错误！")
            for rule in rules:
                rule_type_ids = list(rule.keys())
                utils.green_print(rule_type_ids)
                for rule_type_id in rule_type_ids:
                    if not self.get_count({"$or": [{"related_ids": rule_type_id, "type": TagType.RuleType.value[0]},
                                                   {"id": rule_type_id, "type": TagType.RuleType.value[0]}]}):
                        raise Exception("规则类型不存在！")

    def check_extracts(self, extracts):
        if extracts:
            if not isinstance(extracts, list):
                raise Exception("extracts参数类型错误！")
            for extract in extracts:
                if not isinstance(extract, dict):
                    raise Exception("extracts参数错误！")

                graph_type = extract.get("graph_type")
                if not self.get_count({"id": graph_type}):
                    raise Exception("图谱类型不存在！")

                table = extract.get("table")
                if table not in ["label_entity", "label_chain", "knowledge_entity", "knowledge_chain"]:
                    raise Exception("extracts.table参数错误！")

                id = extract.get("id")
                if not NlpMongo("%s.%s" % ("nlp", table)).get_coll().find_one(
                        {"_id": self.create_objectid(id), "is_enable": True}):
                    raise Exception("实体或链不存在！")

                rules = extract.get("rules")
                chain_rules = extract.get("chain_rules")
                self.check_rules(rules)
                self.check_rules(chain_rules)

    # 查询条件
    # def get_query_params(self, handler, *args, **kwargs):
    #     query_params = {}
    #
    #     # 关键词匹配
    #     keyword = handler.get_argument("keyword", None)
    #
    #     # 标签中文名
    #     zh_name = handler.get_argument("zh_name", None)
    #
    #     # 提取方法
    #     extract_type = handler.get_argument("extract_type", None)
    #
    #     # 案由选择
    #     cause_id = handler.get_argument("cause_id", None)
    #
    #     # 法律查询
    #     law_id = handler.get_argument("law_id", None)
    #
    #     # 标签名和标签别名查询
    #     if keyword != None and keyword != "":
    #         query_params.update({"$or": [{"zh_name": {"$regex": keyword}}, {"alias_name": {"$regex": keyword}}]})
    #
    #     query_params.update({"type": handler.type})
    #
    #     if zh_name != None and zh_name != "":
    #         query_params.update({"zh_name": zh_name})
    #
    #     if extract_type != None and extract_type != "":
    #         if extract_type == "0":
    #             query_params.update({"extract_type": None})
    #         else:
    #             query_params.update({"extract_type": extract_type})
    #
    #     if cause_id != None and cause_id != "":
    #         tag_ids = TagChainModel().search_cause_tag_ids(cause_id)
    #         if query_params.get("$or"):
    #             query_params.update({"$and": [
    #                 {"$or": query_params.get("$or")},
    #                 {"$or": [{"id": {"$in": tag_ids}}, {"related_ids": {"$in": tag_ids}}]}]})
    #             del query_params["$or"]
    #         else:
    #             query_params.update({"$or": [{"id": {"$in": tag_ids}}, {"related_ids": {"$in": tag_ids}}]})
    #
    #     if law_id != None and law_id != "":
    #         query_params.update({"laws": law_id})
    #
    #     return query_params

    def search_read(self, page=1, page_size=10, *args, **kwargs):
        query_params = kwargs.get("query_params")
        type = query_params.get("type")
        _project = kwargs.get("_project")
        if _project:
            if isinstance(kwargs.get("_project"), str):
                try:
                    _project = json.loads(kwargs.get("_project"))
                except:
                    raise Exception("_project参数格式错误！")
            elif isinstance(kwargs.get("_project"), dict):
                _project = kwargs.get("_project")
            else:
                raise Exception("_project参数格式错误！")
            _project.update({"alias_name": 1, "related_ids": 1})
            kwargs["_project"] = _project
        objs, pager = super(TagModel, self).search_read(page, page_size, *args, **kwargs)

        if _project:
            # if _project.get("q_nums"):
            #     # 构造查询参数，检索问题库
            #     related_ids = []
            #     for obj in objs:
            #         tag_id = obj.get("id")
            #         tag_related_ids = obj.get("related_ids") or []
            #         tag_related_ids.append(tag_id)
            #         related_ids = related_ids + tag_related_ids
            #     query_params = es_models.LawQuestionV3().get_title_query_params()
            #     query_params["query"]["filtered"]["filter"]["bool"]["must"].append({
            #         "terms": {"lawTags": related_ids}
            #     })
            #     questions = es_models.LawQuestionV3().blank_search(pager_flag=False, query_params=query_params,
            #                                                        _source_include=["id", "lawTags"])[0]
            #
            #     question_dict = {}
            #     for question in questions:
            #         if question.get("id") not in question_dict.keys():
            #             question_dict[question.get("id")] = question.get("lawTags")
            #         else:
            #             question_dict[question.get("id")] = question_dict[question.get("id")] + question.get("lawTags")
            #
            #     for obj in objs:
            #         count = 0
            #         tag_id = obj.get("id")
            #         tag_related_ids = obj.get("related_ids") or []
            #         tag_related_ids.append(tag_id)
            #         for k, v in question_dict.items():
            #             if len(list(set(tag_related_ids).intersection(set(v)))) > 0:
            #                 count += 1
            #         zh_name = obj.get("alias_name") or obj.get("zh_name")
            #         obj.update(dict(
            #             q_nums=count,
            #             zh_name=zh_name
            #         ))
            # else:
            for obj in objs:
                zh_name = obj.get("alias_name") or obj.get("zh_name")
                obj.update(dict(
                    zh_name=zh_name
                ))
            return objs, pager

