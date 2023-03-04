# -*- coding: utf-8 -*-

import os
import re
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

    def _get_ner_segments(self, text: str, entities: List[str]) -> List[Tuple]:
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

    def format_ner_to_bio(self, text: str, entities: List[str]) -> str:
        segments = self._get_ner_segments(text, entities)
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

    def format_ner_to_segment(self, text: str, entities: List[str]) -> str:
        segments = self._get_ner_segments(text, entities)
        ret = []
        for segment, label in segments:
            ret.append(f'{segment}\t{label}')
        return '\n'.join(ret)

    def ner(self, text: str, formatter: Optional[NERFormatter] = None):
        if formatter is not None and formatter not in NERFormatter.list_attributes():
            raise ValueError(
                f'Invalid formatter `{formatter}`, please specify formatter from NERFormatter for the NER task.')
        params = {
            'labels': self.label_mapping.keys(),
            'text': text
        }
        prompt = self.template.render(**params)
        ret = self.model.predict(prompt)
        ret['text'] = text
        entity_map = {}
        for match in re.finditer(r'\((?P<entity>.+?)\,\s*(?P<entity_type>.+?)\s*\)', ret['response']):
            entity, entity_type = match.group('entity'), match.group('entity_type')
            entity = re.sub(r'(^[\'"\s]+|[\'"\s]+$)', '', entity)
            entity_type = re.sub(r'(^[\'"\s]+|[\'"\s]+$)', '', entity_type)
            if entity_type not in self.label_mapping:
                continue
            if entity not in text:
                continue
            entity_map[entity] = self.label_mapping[entity_type]
        # find positions
        safe_entities = [re.escape(ent) for ent in entity_map]
        entities = []
        for matched in re.finditer(r'(%s)' % ('|'.join(safe_entities)), text):
            entity = matched.group()
            start, end = matched.span()
            entities.append((start, end, entity, entity_map[entity]))
        ret['result'] = entities
        if formatter is not None:
            if formatter == NERFormatter.BIO:
                ret['formatted_result'] = self.format_ner_to_bio(ret['text'], ret['result'])
            elif formatter == NERFormatter.Segment:
                ret['formatted_result'] = self.format_ner_to_segment(ret['text'], ret['result'])

        return ret

    def tag(self, text: str, formatter=None):
        text = text.replace('\n', '')
        if self.task == Tasks.NER:
            return self.ner(text, formatter)

    def __call__(self, text: str, formatter=None):
        return self.tag(text, formatter=formatter)
