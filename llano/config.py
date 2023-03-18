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


class Tasks(AttributeClass):
    ''' Supported Tasks
    '''
    NER = 'ner'
    Classification = 'classification'
    MultiLabelClassification = 'multilabel_classification'
    DataAugmentation = 'data_augmentation'
    RelationExtraction = 'relation_extraction'


class Languages(AttributeClass):
    ''' Supported Languages
    '''
    ZH_CN = 'zh_cn'
    EN = 'en'


class Formatter(AttributeClass):
    JSONL = 'jsonl'


class NERFormatter(AttributeClass):
    BIO = 'BIO'
    Segment = 'segment'


class OpenAIModels(AttributeClass):
    '''
    OpenAI API: https://platform.openai.com/docs/models/gpt-3-5
    '''
    GPT4 = 'gpt-4'
    GPT4_0314 = 'gpt-4-0314'
    GPT4_32k = 'gpt-4-32k'
    GPT4_32k_0314 = 'gpt-4-32k-0314'
    ChatGPT = 'gpt-3.5-turbo'
    GPT35Turbo = 'gpt-3.5-turbo'
    GPT35Turbo0301 = 'gpt-3.5-turbo-0301'
    TextDavinci003 = 'text-davinci-003'
    TextDavinci002 = 'text-davinci-002'
    TextCurie001 = 'text-curie-001'
    TextBabbage001 = 'text-babbage-001'
    TextAda001 = 'text-ada-001'


OpenAIModelMaxTokensMapping = {
    'gpt-4': 8192,
    'gpt-4-0314': 8192,
    'gpt-4-32k': 32768,
    'gpt-4-32k-0314': 32768,
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-0301': 4096,
    'text-davinci-003': 4097,
    'text-davinci-002': 4097,
    'text-curie-001': 2049,
    'text-babbage-001': 2049,
    'text-ada-001': 2049,
}

OpenAIChatCompletionAPIs = frozenset([
    'gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-4-32k-0314', 'gpt-3.5-turbo', 'gpt-3.5-turbo-0301'
])
