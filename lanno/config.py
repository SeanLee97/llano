# -*- coding: utf-8 -*-

import os
from abc import ABCMeta


PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR = os.path.join(PACKAGE_DIR, "templates")
MAX_LRU_CACHE_SIZE = 100000


class AttributeClass(ABCMeta):
    @classmethod
    def list_attributes(cls):
        return [k for k in cls.__dict__.keys()
                if not k.startswith('__') and not k.endswith('__') and k not in ['list_attributes']]

    @classmethod
    def values(cls):
        return [v for k, v in cls.__dict__.items()
                if not k.startswith('__') and not k.endswith('__') and k not in ['list_attributes']]


class OpenAIModels(AttributeClass):
    '''
    OpenAI API: https://platform.openai.com/docs/models/gpt-3-5
    '''
    ChatGPT = 'gpt-3.5-turbo'
    TextDavinci003 = 'text-davinci-003'
    TextDavinci002 = 'text-davinci-002'


class Tasks(AttributeClass):
    ''' Supported Tasks
    '''
    NER = 'ner'
    Classification = 'classification'


class Languages(AttributeClass):
    ''' Supported Languages
    '''
    ZH_CN = 'zh_cn'
    EN = 'en'


class NERFormatter(AttributeClass):
    BIO = 'BIO'
    Segment = 'segment'
