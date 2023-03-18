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
                         task=Tasks.MultiLabelClassification,
                         language=Languages.EN,
                         label_mapping={
                            'comedy movie': 'comedy',
                            'action movie': 'action',
                            'science movie': 'science',
                            'horror movie': 'horror'})
doc = 'The movie is funny, with plenty of captivating fight scenes.'
hint = 'This domain is film genre'
ret = annotator(doc, hint=hint, formatter=Formatter.JSONL)
print('english output:')
pprint(ret)

# 2. chinese example
annotator = GPTAnnotator(model,
                         task=Tasks.MultiLabelClassification,
                         language=Languages.ZH_CN,
                         label_mapping={
                            "搞笑电影": "comedy",
                            "动作电影": "action",
                            "科幻电影": "science",
                            "恐怖电影": "horror"})
hint = '内容是电影领域的。'
doc = '这部电影打斗部分太精彩了，情节也很搞笑'
ret = annotator(doc, hint=hint, formatter=Formatter.JSONL)
print('chinese output:')
pprint(ret)
