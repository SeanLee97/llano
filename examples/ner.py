# -*- coding: utf-8 -*-

import os
from pprint import pprint

from lanno.config import Tasks, Languages, OpenAIModels, NERFormatter
from lanno import GPTModel, GPTAnnotator

print('All Supported Tasks:', Tasks.list_attributes())
print('All Supported Languages:', Languages.list_attributes())
print('All Supported NERFormatter:', NERFormatter.list_attributes())
print('All Supported OpenAIModels:', OpenAIModels.list_attributes())

api_key = os.getenv('OPENAI_KEY')
model = GPTModel(api_key, model=OpenAIModels.ChatGPT)

# 1. English examples
annotator = GPTAnnotator(model,
                         task=Tasks.NER,
                         language=Languages.EN,
                         label_mapping={
                            "people": 'PEO',
                            'location': 'LOC',
                            'company': 'COM',
                            'organization': 'ORG',
                            'job': 'JOB'})
doc = '''Elon Reeve Musk FRS (/ˈiːlɒn/ EE-lon; born June 28, 1971) is a business magnate and investor. He is the founder, CEO and chief engineer of SpaceX; angel investor, CEO and product architect of Tesla, Inc.; owner and CEO of Twitter, Inc.; founder of The Boring Company; co-founder of Neuralink and OpenAI; and president of the philanthropic Musk Foundation. '''
# w/o hint, w/o formatted result
# ret = annotator(doc)
# w/o hint, w/ formatted result
# ret = annotator(doc, formatter=NERFormatter.BIO)
# w/ hint, w/ formatted result
ret = annotator(doc, hint='the entity type `job` is job title such as CEO, founder, boss.', formatter=NERFormatter.BIO)
print('English output:')
pprint(ret)

# 2. Chinese examples
annotator = GPTAnnotator(model,
                         task=Tasks.NER,
                         language=Languages.ZH_CN,
                         label_mapping={
                            '人名': 'PEO',
                            '地名': 'LOC',
                            '公司名': 'COM',
                            '机构名': 'ORG',
                            '身份': 'ID'})
doc = '''埃隆·里夫·马斯克（Elon Reeve Musk） [107]  ，1971年6月28日出生于南非的行政首都比勒陀利亚，企业家、工程师、慈善家、美国国家工程院院士。他同时兼具南非、加拿大和美国三重国籍。埃隆·马斯克本科毕业于宾夕法尼亚大学，获经济学和物理学双学位。1995年至2002年，马斯克与合伙人先后办了三家公司，分别是在线内容出版软件“Zip2”、电子支付“X.com”和“PayPal”。'''

# ret = annotator(doc)  # w/o hint, w/o formatter
# ret = annotator(doc, formatter=NERFormatter.BIO)  # w/o hint, w/ formatter
ret = annotator(doc, hint='身份表示从事职位的头衔或社会地位等，如：老板，董事长，作家，理事长等', formatter=NERFormatter.BIO)
print('Chinese output:')
pprint(ret)
