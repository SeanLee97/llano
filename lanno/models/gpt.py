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
                 temperature: float = 0.8,
                 max_tokens: int = 4000,
                 top_p: float = 1,
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
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop
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
        if len(tokens) > self.max_tokens:
            raise ValueError(
                f'OOT (Out Of Tokens)! the current input text has `{len(tokens)}` tokens, '
                'which is greater than the max_tokens {self.max_tokens}')
        data = self.get_output_template()
        data['request'] = {'prompt': text}
        meta = {}
        if self.model == OpenAIModels.ChatGPT:
            resp = self._predict(messages=[{"role": "user", "content": text}],
                                 max_tokens=self.max_tokens - len(tokens))
            data["response"] = resp["choices"][0]["message"]["content"]
            meta["role"] = resp["choices"][0]["message"]["role"]
        else:
            resp = self._predict(prompt=text, max_tokens=self.max_tokens - len(tokens))
            data["response"] = resp["choices"][0]["text"]
        meta.update(resp["usage"])
        data['meta'] = meta
        return data
