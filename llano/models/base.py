# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Dict


class BaseModel(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.model = None

    @abstractmethod
    def predict(self):
        raise NotImplementedError

    def get_output_template(self) -> Dict:
        return {
            'request': None,
            'meta': None,
            'response': None,
            'result': None
        }
