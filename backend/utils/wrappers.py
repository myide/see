# -*- coding: utf-8 -*-
import time
import logging
from functools import wraps
from django.db import close_old_connections
from rest_framework.exceptions import ParseError

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start = time.time()
        try:
            result = func(*args,**kwargs)
            end = time.time()
            runtime = end - start
            return result, '%.3f' % runtime
        except Exception as e:
            logging.error('programe running err:{}',format(e))
    return wrapper

def close_old_conn(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            close_old_connections()
            return func(*args,**kwargs)
        except Exception as e:
            logging.error('programe running err:{}',format(e))
    return wrapper

def catch_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ParseError(e)
    return wrapper
