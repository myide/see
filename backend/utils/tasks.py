# -*- coding: utf-8 -*-
from celery import task
from .mail import Mail

@task
def send_mail(**kwargs):
    return Mail.send(kwargs)
