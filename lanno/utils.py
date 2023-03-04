# -*- coding: utf-8 -*-

import time
import functools


def with_taken_time(func):
    ''' Append taken time to data
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        data = func(*args, **kwargs)
        data['taken_time'] = round(time.time() - start_time, 5)
        return data
    return wrapper
