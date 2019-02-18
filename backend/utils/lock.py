#coding:utf-8

import redis
import time
from django.conf import settings

locals().update(settings.LOCK)

class RedisLock(object):

    pool = redis.ConnectionPool(host=host, port=port, db=db)
    redis_client = redis.Redis(connection_pool=pool)
    timeout = timeout

    @classmethod
    def delete_lock(cls, key):
        cls.redis_client.delete(key)

    @classmethod
    def set_lock(cls, key, value):
        return cls.redis_client.setnx(key, value)

    @classmethod
    def locked(cls, key):
        now = int(time.time())
        if cls.set_lock(key, now):  # 加锁成功
            return True
        else:
            lock_time = cls.redis_client.get(key)
            if now > int(lock_time) + cls.timeout:  # （比较当前时间和锁的时间）如果已过期，释放锁
                cls.delete_lock(key)
                return cls.set_lock(key, now)  # 重新加锁
            return False