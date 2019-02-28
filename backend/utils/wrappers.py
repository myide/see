import time,logging
from django.db import close_old_connections

def timer(func):
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
    def wrapper(*args,**kwargs):
        try:
            close_old_connections()
            return func(*args,**kwargs)
        except Exception as e:
            logging.error('programe running err:{}',format(e))
    return wrapper