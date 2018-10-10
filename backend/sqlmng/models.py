#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from account.models import User
from django.contrib.auth.models import Group
from utils.basemodels import Basemodel
# Create your models here.

class Dbconf(Basemodel):
    ENVS = (
        ('prd', u'生产环境'),
        ('test', u'测试环境')
    )
    related_user = models.ManyToManyField(User, null=True, blank=True)
    user = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=16)
    port = models.CharField(max_length=5)
    env = models.CharField(max_length=8, choices=ENVS)
    class Meta:
        unique_together = ('name', 'host', 'env')

class Inceptsql(Basemodel):
    STATUS = (
        (-3, u'已回滚'),
        (-2, u'已暂停'),
        (-1, u'待执行'),
        (0, u'已执行'),
        (1, u'已放弃'),
        (2, u'执行失败'),
    )
    ENVS = (
        ('prd', u'生产环境'),
        ('test', u'测试环境')
    )
    users = models.ManyToManyField(User)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)
    db = models.ForeignKey(Dbconf, on_delete=models.CASCADE)
    is_manual_review = models.BooleanField(default=False, verbose_name='有流程')
    handleable = models.BooleanField(default=False, verbose_name='审批状态')
    commiter = models.CharField(max_length=20, null=True, blank=True)
    sql_content = models.TextField()
    env = models.CharField(max_length=8, choices=ENVS)
    treater = models.CharField(max_length=20)
    status = models.IntegerField(default=-1, choices=STATUS)
    execute_errors = models.TextField(default='', null=True, blank=True)
    exe_affected_rows = models.CharField(max_length=10, null=True, blank=True)
    roll_affected_rows = models.CharField(max_length=10, null=True, blank=True)
    rollback_opid = models.TextField(null=True, blank=True)
    rollback_db = models.CharField(max_length=100, null=True, blank=True)
    inception_detail = models.TextField(default='', null=True, blank=True, verbose_name='inception详情')

class Step(Basemodel):
    STATUS = (
        (-1, u'终止'),
        (0, u'待处理'),
        (1, u'通过'),
        (2, u'驳回'),
        (3, u'放弃')
    )
    work_order = models.ForeignKey(Inceptsql, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, choices=STATUS)

class Suggestion(Basemodel):
    work_order = models.ForeignKey(Inceptsql, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

class Strategy(Basemodel):
    users = models.ManyToManyField(User, null=True, blank=True)
    is_manual_review = models.BooleanField(default=False, verbose_name='有流程')

class ForbiddenWords(Basemodel):
    forbidden_words = models.TextField(null=True, blank=True)

class AuthRules(Basemodel):
    ROLES = (
        ('developer_supremo', u'总监'),
        ('developer_manager', u'经理'),
        ('developer', u'研发'),
    )
    ENVS = (
        ('prd', u'生产环境'),
        ('test', u'测试环境')
    )
    is_manual_review = models.BooleanField(verbose_name='有流程')
    role = models.CharField(max_length=32, choices=ROLES)
    env = models.CharField(max_length=8, choices=ENVS)
    reject = models.BooleanField()
    execute = models.BooleanField()
    rollback = models.BooleanField()
    approve = models.BooleanField()
    disapprove = models.BooleanField()
