# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from .models import *
from .data import *

class AppMap(object):

    @property
    def data_list(self):
        return (
            (InceptionConnection, inception_conn),
            (SqlSettings, sql_settings)
        )

    def handle_data(self, model, data):
        queryset = model.objects.all()
        if queryset.count() is not 1:
            queryset.delete()
            model.objects.create(**data[0])

    def sqlmng(self):
        for item in self.data_list:
            self.handle_data(item[0], item[1])

@receiver(post_migrate)
def callback(sender, **kwargs):
    sender_name = sender.name
    func = getattr(AppMap(), sender_name, None)
    if func:
        func()