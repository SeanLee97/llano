# -*- coding: utf-8 -*-

import os
from pprint import pprint

from llano.config import Tasks, Languages, OpenAIModels, Formatter
from llano import GPTModel, GPTAnnotator

print('All Supported Tasks:', Tasks.list_attributes())
print('All Supported Languages:', Languages.list_attributes())
print('All Supported Formatter:', Formatter.list_attributes())
print('All Supported OpenAIModels:', OpenAIModels.list_attributes())

api_key = os.getenv('OPENAI_KEY')
model = GPTModel(api_key, model=OpenAIModels.ChatGPT)

# 1. english example
annotator = GPTAnnotator(model,
                         task=Tasks.RelationExtraction,
                         language=Languages.EN,
                         label_mapping={
                            "work at": 'work_at',
                            'live in': 'live_in'})
doc = '''Mr. Li currently work for HelloWorld Tech which is a tech company. And he live in Shanghai.'''
ret = annotator(doc, hint=None, formatter=Formatter.JSONL)
print('english output:')
pprint(ret)

# 2. chinese example
annotator = GPTAnnotator(model,
                         task=Tasks.RelationExtraction,
                         language=Languages.ZH_CN,
                         label_mapping={
                            "工作在": 'work_at',
                            '居住在': 'live_in'})
doc = '李华住在上海，目前在HelloWorld公司上班'
hint = '主语和宾语都要具体的名称，不要指代词'
ret = annotator(doc, hint=hint, formatter=Formatter.JSONL)
print('chinese output:')
pprint(ret)
