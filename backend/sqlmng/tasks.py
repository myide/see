#coding=utf-8
import time
from celery import task
from django.conf import settings
from account.models import User
from utils.lock import RedisLock
from .models import Inceptsql
from .mixins import Handle

locals().update(settings.CELERY_BUSINESS_PARAMS)

class HandleAction(Handle):

    def __init__(self, instance=None):
        self.steps = instance.workorder.step_set.all()

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def handle_result(self, instance, affected_rows, step_number, timer, user_id, handle_type):
        user = self.get_user(user_id)
        instance.execute_time = timer
        instance.affected_rows = affected_rows
        self.replace_remark(instance, handle_type, user)
        self.handle_workflow(2, 1, step_number, instance)
        self.save_instance(instance)
        RedisLock.delete_lock(instance.id)
        self.mail(instance, handle_type, user)

@task
def task_worker(pk, step_number, handle_type, user_id):
    instance = Inceptsql.objects.get(pk=pk)
    Handle.save_instance(instance, 6)
    action = HandleAction(instance)
    handle = getattr(action, handle_type)
    (instance, affected_rows), timer = handle(instance)
    action.handle_result(instance, affected_rows, step_number, timer, user_id, handle_type)

@task
def cron_task():
    current_time = time.strftime(date_format, time.localtime(time.time()))
    crontab_tasks = Inceptsql.objects.filter(is_manual_review=1, cron_time=current_time, status=5)
    if not crontab_tasks:
        return
    cron_user, _ = User.objects.get_or_create(username=username)
    for instance in crontab_tasks:
        step_admin = HandleAction(instance).steps[1]
        if step_admin.status == 1:
            task_worker.delay(instance.id, 3, action_type, cron_user.id)
