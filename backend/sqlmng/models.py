#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from account.models import User
from django.contrib.auth.models import Group
from utils.basemodels import Basemodel
# Create your models here.

class Dbconf(Basemodel):
    GENDER_CHOICES = (
        ('prd', u'生产环境'),
        ('test', u'测试环境')
    )
    user = models.CharField(max_length = 128)
    password = models.CharField(max_length = 128)
    host = models.CharField(max_length = 16)
    port = models.CharField(max_length = 5)
    env = models.CharField(max_length = 20, choices = GENDER_CHOICES)
    class Meta:
        unique_together = ('name', 'host', 'env')

class Inceptsql(Basemodel):
    SQL_STATUS = (
        (-3, u'已回滚'),
        (-2, u'已暂停'),
        (-1, u'待执行'),
        (0, u'已执行'),
        (1, u'已放弃'),
        (2, u'执行失败'),
    )

    ENV = (
        ('prd', u'生产环境'),
        ('test', u'测试环境')
    )

    users = models.ManyToManyField(User)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)
    db = models.ForeignKey(Dbconf, on_delete=models.CASCADE)
    commiter = models.CharField(max_length = 20, null=True, blank=True)
    sql_content = models.TextField()
    env = models.CharField(max_length = 20, choices = ENV)
    treater = models.CharField(max_length = 20)
    status = models.IntegerField(default = -1, choices = SQL_STATUS)
    execute_errors = models.TextField(default='', null=True, blank=True)
    #execute_time = models.CharField(max_length = 11)
    exe_affected_rows = models.CharField(max_length = 10, null=True, blank=True)
    roll_affected_rows = models.CharField(max_length = 10, null=True, blank=True)
    rollback_opid = models.TextField(blank = True, null = True)
    rollback_db = models.CharField(max_length = 100, null=True, blank=True)
