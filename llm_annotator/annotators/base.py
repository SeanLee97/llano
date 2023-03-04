# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class BaseAnnotator(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.model = None

    @abstractmethod
    def tag(self):
        raise NotImplementedError
