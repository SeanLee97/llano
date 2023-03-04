# -*- coding: utf-8 -*-

from typing import Dict, Union
from functools import partial, lru_cache

import tiktoken
import openai

from .base import BaseModel
from ..config import OpenAIModels, MAX_LRU_CACHE_SIZE
from ..utils import with_taken_time


class GPTModel(BaseModel):
    def __init__(self,
                 api_key: str,
                 model: OpenAIModels = OpenAIModels.ChatGPT,
                 temperature: float = 0.7,
                 max_tokens: int = 4000,
                 top_p: float = 0.1,
                 frequency_penalty: float = 0,
                 presence_penalty: float = 0,
                 stop: Union[str, None] = None,) -> None:
        super().__init__()
        self.tokenizer = tiktoken.encoding_for_model(model)
        self.model = model
        # init openai
        self.max_tokens = max_tokens
        openai.api_key = api_key
        if self.model == OpenAIModels.ChatGPT:
            self._predict = partial(
                openai.ChatCompletion.create,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            self._predict = partial(
                openai.Completion.create,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop
            )

    @lru_cache(maxsize=MAX_LRU_CACHE_SIZE)
    @with_taken_time
    def predict(self, text: str) -> Dict:
        tokens = self.tokenizer.encode(text)
        data = {}
        data['prompt'] = text
        if self.model == OpenAIModels.ChatGPT:
            resp = self._predict(messages=[{"role": "user", "content": text}],
                                 max_tokens=self.max_tokens - len(tokens))
            data["response"] = resp["choices"][0]["message"]["content"]
            data["role"] = resp["choices"][0]["message"]["role"]
        else:
            resp = self._predict(prompt=text, max_tokens=self.max_tokens - len(tokens))
            data["response"] = resp["choices"][0]["text"]
        data.update(resp["usage"])
        return data