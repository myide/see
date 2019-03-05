# -*- coding: utf-8 -*-
from django.db import models
from account.models import User
from utils.basemodels import Basemodel

# Create your models here.

class WorkOrder(Basemodel):
    status = models.BooleanField(default=False, verbose_name='审批状态')

class Step(Basemodel):
    STATUS = (
        (-1, u'终止'),
        (0, u'待处理'),
        (1, u'通过'),
        (2, u'驳回'),
        (3, u'放弃')
    )
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, choices=STATUS)
