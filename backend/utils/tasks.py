#coding=utf-8

from celery import task
from .mail import Mail

@task
def send_mail(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname):
    return Mail.send(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname)
