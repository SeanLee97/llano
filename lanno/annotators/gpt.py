# -*- coding: utf-8 -*-

import os
import re
from copy import deepcopy
from typing import Dict, Optional, List, Tuple

from jinja2 import Template

from ..config import Tasks, Languages, TEMPLATE_DIR, NERFormatter
from ..models import GPTModel
from .base import BaseAnnotator


class GPTAnnotator(BaseAnnotator):
    def __init__(self,
                 model: GPTModel,
                 task: Tasks,
                 label_mapping: Dict,
                 language: Languages,
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
    def make_ner_extraction_regex(labels):
        return re.compile(
            r'\((?P<entity>((?!\)).)+)\,'  # entity
            r'.*?(?P<entity_type>(%s)).*?\)' % '|'.join(  # entity_type
                [re.escape(k) for k in labels]))

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
            entity = re.sub(r'(^[\'"\s]+|[\'"\s]+$)', '', entity)
            entity_type = re.sub(r'(^[\'"\s]+|[\'"\s]+$)', '', entity_type)
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

    def tag(self, text: str, hint: Optional[str] = None, formatter=None):
        text = text.replace('\n', '')
        if self.task == Tasks.NER:
            return self.ner(text, hint=hint, formatter=formatter)

    def __call__(self, text: str, hint: Optional[str] = None, formatter=None):
        return self.tag(text, hint=hint, formatter=formatter)
