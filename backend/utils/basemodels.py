#coding=utf-8
from django.db import models

class Basemodel(models.Model):
    '''
       基础表(抽象类)
    '''
    name = models.CharField(default='', null=True, blank=True, max_length=128, verbose_name='名字')
    createtime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updatetime = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['-id']
