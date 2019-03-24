# -*- coding: utf-8 -*-
import time
from celery import task
from django.conf import settings
from account.models import User
from utils.lock import RedisLock
from utils.wrappers import close_old_conn
from utils.basemixins import AppellationMixin
from .models import InceptionWorkOrder
from .mixins import Handle, MailMixin

locals().update(settings.CELERY_BUSINESS_PARAMS)

class HandleAction(MailMixin, Handle):

    def __init__(self, instance=None):
        self.steps = instance.work_order.step_set.all()

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @close_old_conn
    def handle_result(self, instance, affected_rows, step_number, timer, user_id, _type):
        user = self.get_user(user_id)
        instance.execute_time = timer
        instance.affected_rows = affected_rows
        self.replace_remark(instance, _type, user)
        self.handle_workflow(2, 1, step_number, instance)
        self.save_instance(instance)
        RedisLock.delete_lock(instance.id)
        self.mail(instance, _type, user, self.name_mail_inception)

@task
def task_worker(pk, step_number, _type, user_id):
    instance = InceptionWorkOrder.objects.get(pk=pk)
    status = 7 if _type == AppellationMixin.urn_rollback else 6
    Handle.save_instance(instance, status)
    action = HandleAction(instance)
    handle = getattr(action, _type)
    (instance, affected_rows), timer = handle(instance)
    action.handle_result(instance, affected_rows, step_number, timer, user_id, _type)

@task
def cron_task():
    current_time = time.strftime(date_format, time.localtime(time.time()))
    crontab_tasks = InceptionWorkOrder.objects.filter(cron_time=current_time, status=5)
    if not crontab_tasks:
        return
    cron_user, _ = User.objects.get_or_create(username=username)
    for instance in crontab_tasks:
        _type = instance.type or handle_type
        task_worker.delay(instance.id, 3, _type, cron_user.id)