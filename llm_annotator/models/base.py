# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class BaseModel(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.model = None

    @abstractmethod
    def predict(self):
        raise NotImplementedError
