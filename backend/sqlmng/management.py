# -*- coding: utf-8 -*-
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from .models import *
from .data import *

class AppMap(object):

    content_type = 'dbconf'
    perm = settings.PERM_DATABASE

    @property
    def data_list(self):
        return (
            (InceptionConnection, inception_conn),
            (SqlSettings, sql_settings)
        )

    def handle_data(self, model, data, count):
        queryset = model.objects.filter(**data)
        if queryset.count() is not count:
            queryset.delete()
            model.objects.create(**data)

    def sqlmng(self):
        for item in self.data_list:
            self.handle_data(item[0], item[1][0], 1)

    def auth(self):
        content_type = ContentType.objects.filter(model=self.content_type)
        if content_type:
            data = {
                'name': 'Can manage target database',
                'content_type': content_type[0],
                'codename': self.perm
            }
            self.handle_data(Permission, data, 1)

@receiver(post_migrate)
def callback(sender, **kwargs):
    sender_name = sender.name.split('.')[-1]
    func = getattr(AppMap(), sender_name, None)
    if func:
        func()