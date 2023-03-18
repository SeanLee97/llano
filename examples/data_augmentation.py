# -*- coding: utf-8 -*-

import os
from pprint import pprint

from llano.config import Tasks, Languages, OpenAIModels, Formatter
from llano import GPTModel, GPTAnnotator

print('All Supported Tasks:', Tasks.list_attributes())
print('All Supported Languages:', Languages.list_attributes())
print('All Supported Formatter:', Formatter.list_attributes())
print('All Supported OpenAIModels:', OpenAIModels.list_attributes())

api_keys = [os.getenv('OPENAI_KEY')]
model = GPTModel(api_keys, model=OpenAIModels.ChatGPT)

# 1. english example
annotator = GPTAnnotator(model,
                         task=Tasks.DataAugmentation,
                         language=Languages.EN)
doc = 'The weather is very good today'
ret = annotator(doc, hint=None, formatter=Formatter.JSONL, size=5)
print('english output:')
pprint(ret)

# 2. chinese example
annotator = GPTAnnotator(model,
                         task=Tasks.DataAugmentation,
                         language=Languages.ZH_CN)
doc = '今天天气太好了'
ret = annotator(doc, hint=None, formatter=Formatter.JSONL, size=5)
print('chinese output:')
pprint(ret)
