# -*- coding: utf-8 -*-

import os
import re
import json
from copy import deepcopy
from typing import Dict, Optional, List, Tuple

from jinja2 import Template

from ..config import Tasks, Languages, Formatter, NERFormatter, TEMPLATE_DIR
from ..models import GPTModel
from .base import BaseAnnotator


class GPTAnnotator(BaseAnnotator):
    def __init__(self,
                 model: GPTModel,
                 task: Tasks,
                 language: Languages,
                 label_mapping: Optional[Dict] = None,
                 **kwargs) -> None:
        super().__init__()
        self.model = model
        self.task = task
        self.label_mapping = label_mapping
        # load template
        with open(os.path.join(TEMPLATE_DIR, 'texts', f'{task}.{language}.jinja')) as reader:
            self.template = Template(reader.read())

    @staticmethod
    def get_all_ner_segments(text: str, entities: List[str]) -> List[Tuple]:
        prev_start = 0
        segments = []
        for start, end, entity, entity_type in entities:
            if start > prev_start:
                segments.append((text[prev_start: start], 'O'))
            segments.append((entity, entity_type))
            prev_start = end
        if prev_start < len(text):
            segments.append((text[prev_start:], 'O'))
        return segments

    @staticmethod
    def format_ner_to_bio(text: str, entities: List[str]) -> str:
        segments = GPTAnnotator.get_all_ner_segments(text, entities)
        ret = []
        for segment, label in segments:
            if label == 'O':
                ret.append('\n'.join([f'{w}\t{t}' for w, t in zip(segment, [label] * len(segment))]))
            else:
                head = f'{segment[0]}\tB-{label}'
                if len(segment) > 1:
                    head += '\n'
                    head += '\n'.join([f'{w}\tI-{t}' for w, t in zip(segment[1:], [label] * len(segment[1:]))])
                ret.append(head)
        return '\n'.join(ret)

    @staticmethod
    def format_ner_to_segment(text: str, entities: List[str]) -> str:
        segments = GPTAnnotator.get_all_ner_segments(text, entities)
        ret = []
        for segment, label in segments:
            ret.append(f'{segment}\t{label}')
        return '\n'.join(ret)

    @staticmethod
    def make_ner_extraction_regex(labels: List[str]):
        # sort by label length to support overlap labels
        labels = sorted(labels, key=lambda x: len(x), reverse=True)
        return re.compile(
            r'\((?P<entity>((?!\)).)+)\,'  # entity
            r'.*?(?P<entity_type>(%s)).*?\)' % '|'.join(  # entity_type
                [re.escape(k) for k in labels]))

    @staticmethod
    def make_classification_extraction_regex(labels: List[str]):
        # sort by label length to support overlap labels
        labels = sorted(labels, key=lambda x: len(x), reverse=True)
        return re.compile(
            r'(%s)+' % '|'.join([re.escape(label) for label in labels])
        )

    @staticmethod
    def make_data_augmentation_regex():
        return re.compile(
            r'(?P<ordial>[0-9]+?)\.?(?P<sentence>.+)\n'
        )

    @staticmethod
    def make_relation_extraction_regex(labels: List[str]):
        # sort by label length to support overlap labels
        labels = sorted(labels, key=lambda x: len(x), reverse=True)
        label_concat = "|".join([re.escape(k) for k in labels])
        return re.compile(
            r'\((?P<subject>((?!\)).)+)\,'  # subject
            rf'[\'"\s]*?(?P<predicate>({label_concat}))[\'"\s]*?\,'  # predicate
            r'(?P<object>((?!\)).)+)\)'  # object
        )

    @staticmethod
    def re_strip(text: str) -> str:
        return re.sub(r'(^[\'"\s]+|[\'"\s]+$)', '', text)

    def ner(self, text: str, hint: Optional[str] = None, formatter: Optional[NERFormatter] = None):
        if formatter is not None and formatter not in NERFormatter.values():
            raise ValueError(
                f'Invalid formatter `{formatter}`, please specify formatter from NERFormatter for the NER task.')
        prompt = self.template.render(
            labels=list(self.label_mapping.keys()),
            text=text,
            hint=hint)
        resp = self.model.predict(prompt)
        ret = deepcopy(resp)
        ret['result'] = {}
        ret['result']['text'] = text
        entity_map = {}
        pair_regex = GPTAnnotator.make_ner_extraction_regex(self.label_mapping.keys())
        for match in pair_regex.finditer(ret['response']):
            entity, entity_type = match.group('entity'), match.group('entity_type')
            entity = self.re_strip(entity)
            entity_type = self.re_strip(entity_type)
            if entity_type not in self.label_mapping:
                continue
            if entity not in text:
                continue
            entity_map[entity] = self.label_mapping[entity_type]
        if not entity_map:
            return ret
        # find positions
        safe_entities = [re.escape(ent) for ent in entity_map]
        entities = []
        for matched in re.finditer(r'(%s)' % ('|'.join(safe_entities)), text):
            entity = matched.group()
            start, end = matched.span()
            entities.append((start, end, entity, entity_map[entity]))
        ret['result']['entities'] = entities
        if formatter is not None:
            if formatter == NERFormatter.BIO:
                ret['result']['formatted_result'] = GPTAnnotator.format_ner_to_bio(
                    ret['result']['text'], ret['result']['entities'])
            elif formatter == NERFormatter.Segment:
                ret['result']['formatted_result'] = GPTAnnotator.format_ner_to_segment(
                    ret['result']['text'], ret['result']['entities'])
        return ret

    def classification(self,
                       text: str,
                       hint: Optional[str] = None,
                       formatter: Optional[Formatter] = None,
                       is_multilabel: bool = False):
        if formatter is not None and formatter not in Formatter.values():
            raise ValueError(
                f'Invalid formatter `{formatter}`, '
                'please specify formatter from Formatter for the classification task.')
        prompt = self.template.render(
            labels=list(self.label_mapping.keys()),
            text=text,
            hint=hint)
        resp = self.model.predict(prompt)
        ret = deepcopy(resp)
        ret['result'] = {}
        ret['result']['text'] = text
        label_regex = self.make_classification_extraction_regex(list(self.label_mapping.keys()))
        labels = label_regex.findall(ret['response'])
        if not labels:
            return ret
        ret['result']['label'] = labels if is_multilabel else labels[0]
        if formatter is not None:
            if formatter == Formatter.JSONL:
                ret['result']['formatted_result'] = json.dumps(
                    {'text': ret['result']['text'], 'label': ret['result']['label']}, ensure_ascii=False)
        return ret

    def data_augmentation(self,
                          text: str,
                          hint: Optional[str] = None,
                          formatter: Optional[Formatter] = None,
                          size: int = 1):
        if formatter is not None and formatter not in Formatter.values():
            raise ValueError(
                f'Invalid formatter `{formatter}`, '
                'please specify formatter from Formatter for the data augmentation task.')
        prompt = self.template.render(
            text=text,
            hint=hint,
            size=size)
        resp = self.model.predict(prompt)
        ret = deepcopy(resp)
        ret['result'] = {}
        ret['result']['text'] = text
        regex = self.make_data_augmentation_regex()
        sentences = []
        for matched in regex.finditer(ret['response'].rstrip('\n') + '\n'):
            sentences.append(matched.group('sentence').strip())
        ret['result']['sentences'] = sentences
        if formatter is not None:
            if formatter == Formatter.JSONL:
                ret['result']['formatted_result'] = json.dumps(
                    {'text': ret['result']['text'], 'sentences': ret['result']['sentences']}, ensure_ascii=False)
        return ret

    def relation_extraction(self,
                            text: str,
                            hint: Optional[str] = None,
                            formatter: Optional[Formatter] = None):
        if formatter is not None and formatter not in Formatter.values():
            raise ValueError(
                f'Invalid formatter `{formatter}`, '
                'please specify formatter from Formatter for the classification task.')
        prompt = self.template.render(
            labels=list(self.label_mapping.keys()),
            text=text,
            hint=hint)
        resp = self.model.predict(prompt)
        ret = deepcopy(resp)
        ret['result'] = {}
        ret['result']['text'] = text
        regex = self.make_relation_extraction_regex(list(self.label_mapping.keys()))
        triples = []
        for matched in regex.finditer(ret['response']):
            triples.append((self.re_strip(matched.group('subject')),
                            self.re_strip(matched.group('predicate')),
                            self.re_strip(matched.group('object'))))
        ret['result']['triples'] = triples
        if formatter is not None:
            if formatter == Formatter.JSONL:
                ret['result']['formatted_result'] = json.dumps(ret['result'], ensure_ascii=False)
        return ret

    def tag(self, text: str, hint: Optional[str] = None, formatter=None, **kwargs):
        text = text.replace('\n', '')
        if self.task == Tasks.NER:
            return self.ner(text, hint=hint, formatter=formatter)
        elif self.task == Tasks.Classification:
            return self.classification(text, hint=hint, formatter=formatter, is_multilabel=False)
        elif self.task == Tasks.MultiLabelClassification:
            return self.classification(text, hint=hint, formatter=formatter, is_multilabel=True)
        elif self.task == Tasks.DataAugmentation:
            return self.data_augmentation(text, hint=hint, formatter=formatter, size=kwargs.get('size', 1))
        elif self.task == Tasks.RelationExtraction:
            return self.relation_extraction(text, hint=hint, formatter=formatter)

    def __call__(self, text: str, hint: Optional[str] = None, formatter=None, **kwargs):
        return self.tag(text, hint=hint, formatter=formatter, **kwargs)
