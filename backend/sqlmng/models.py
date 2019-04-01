# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from account.models import User
from django.contrib.auth.models import Group
from utils.basemodels import Basemodel
from workflow.models import WorkOrder
# Create your models here.

ENVS = (
    ('prd', u'生产环境'),
    ('test', u'测试环境')
)

class Cluster(Basemodel):
    class Meta:
        unique_together = ['name']

class DbConf(Basemodel):
    related_user = models.ManyToManyField(User, null=True, blank=True)
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=64)
    port = models.CharField(max_length=5)
    env = models.CharField(max_length=8, choices=ENVS)
    class Meta:
        unique_together = ('name', 'host', 'env', 'cluster')
        ordering = ['-id']

class InceptionWorkOrder(Basemodel):
    STATUS = (
        (-3, u'回滚成功'),
        (-2, u'已暂停'),
        (-1, u'待执行'),
        (0, u'执行成功'),
        (1, u'已放弃'),
        (2, u'任务异常'),
        (3, u'审批通过'),
        (4, u'审批驳回'),
        (5, u'已定时'),
        (6, u'执行中'),
        (7, u'回滚中')
    )
    users = models.ManyToManyField(User)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE)
    db = models.ForeignKey(DbConf, on_delete=models.CASCADE)
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE)
    is_manual_review = models.BooleanField(default=False, verbose_name='有流程')
    commiter = models.CharField(max_length=64, null=True, blank=True)
    sql_content = models.TextField()
    env = models.CharField(max_length=8, choices=ENVS)
    type = models.CharField(max_length=32, null=True, blank=True)
    treater = models.CharField(max_length=64)
    status = models.IntegerField(default=-1, choices=STATUS)
    execute_errors = models.TextField(default='', null=True, blank=True)
    execute_time = models.CharField(max_length = 32, null=True, blank=True)
    rollback_time = models.CharField(max_length = 32, null=True, blank=True)
    affected_rows = models.CharField(max_length=16, null=True, blank=True)
    rollback_opid = models.TextField(null=True, blank=True)
    rollback_db = models.CharField(max_length=128, null=True, blank=True)
    rollback_able = models.BooleanField(default=False, verbose_name='可回滚')
    cron_time = models.CharField(max_length=64, null=True, blank=True)
    handle_result = models.TextField(default='', null=True, blank=True, verbose_name='处理详情')
    handle_result_check = models.TextField(default='', null=True, blank=True, verbose_name='审核详情')
    handle_result_execute = models.TextField(default='', null=True, blank=True, verbose_name='执行详情')
    handle_result_rollback = models.TextField(default='', null=True, blank=True, verbose_name='回滚详情')

class Suggestion(Basemodel):
    work_order = models.ForeignKey(InceptionWorkOrder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

class Strategy(Basemodel):
    is_manual_review = models.BooleanField(default=False, verbose_name='有流程')

class SqlSettings(Basemodel):
    forbidden_words = models.TextField(null=True, blank=True, default='')
    sql_count_limit = models.IntegerField(null=True, blank=True, default=1000)

class AuthRules(Basemodel):
    ROLES = (
        ('developer_supremo', u'总监'),
        ('developer_manager', u'经理'),
        ('developer', u'研发'),
    )
    is_manual_review = models.BooleanField(verbose_name='有流程')
    role = models.CharField(max_length=32, choices=ROLES)
    env = models.CharField(max_length=8, choices=ENVS)
    reject = models.BooleanField()
    cron = models.BooleanField()
    execute = models.BooleanField()
    rollback = models.BooleanField()
    approve = models.BooleanField()
    disapprove = models.BooleanField()

class InceptionVariables(Basemodel):
    param = models.CharField(max_length=64, null=True, blank=True)
    default = models.CharField(max_length=16, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    class Meta:
        ordering = ['id']

class InceptionConnection(Basemodel):
    host = models.CharField(max_length=64, null=True, blank=True, default='127.0.0.1')
    port = models.CharField(max_length=5, null=True, blank=True, default=6669)

class MailActions(Basemodel):
    value = models.BooleanField(default=True, verbose_name='是否发送')
    desc_cn = models.CharField(max_length=128, null=True, blank=True)

class DatabaseWorkOrder(Basemodel):
    STATUS = (
        (0, u'待审核'),
        (1, u'审核通过'),
        (2, u'审核驳回'),
        (3, u'放弃')
    )
    commiter = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='commiter')
    treater = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='treater')
    status = models.IntegerField(default=0, choices=STATUS)
    env = models.CharField(max_length=8, null=True, blank=True, choices=ENVS)
    db_cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    db_host = models.CharField(max_length=64, null=True, blank=True)
    db_port = models.CharField(max_length=5, null=True, blank=True)
    db_list = models.TextField(default='', null=True, blank=True)
