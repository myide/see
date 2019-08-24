# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = (
        ('developer_supremo', u'总监'),
        ('developer_manager', u'经理'),
        ('developer', u'研发'),
    )
    leader = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='leader_devs')
    admin_mail = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='admin_devs')
    role = models.CharField(max_length=32, default='developer', choices=ROLES)
    mail_list_extend = models.TextField(null=True, blank=True)
    remark = models.CharField(max_length=128, default='', blank=True)

    class Meta:
        verbose_name_plural = u'用户'

    def __unicode__(self):
        return self.username
