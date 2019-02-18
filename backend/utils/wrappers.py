import time,logging

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