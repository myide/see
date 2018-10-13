#coding=utf8
from rest_framework.exceptions import ParseError
from utils.tasks import send_mail
from utils.basemixins import AppellationMixins
from utils.dbcrypt import prpcrypt
from utils.sqltools import Inception
from .models import *
import re
import json

class PromptMxins(object):
    connect_error = 'MySQL连接异常 '
    forbidden_words = '禁用关键字 '
    exception_sqls = 'SQL语法错误 '
    not_exists_group = '用户的组不存在 '
    executed = 'SQL已执行过'
    approve_warning = '此工单无需重复审批'
    reject_warning = '该工单当前的流转状态不在您这里，无法放弃'
    require_handleable = '该工单未审批，无法操作'
    require_different = '执行人和审批人相同，无法操作'
    require_same = '您不是该工单的审批人，无法审批'

class ActionMxins(AppellationMixins, object):

    def get_reject_step(self, instance):
        user = self.request.user
        if self.has_flow(instance):
            if user.is_superuser:
                return 1 if instance.commiter == user.username else 2
            else:
                role = user.role
                return self.reject_steps.get(role)

    @staticmethod
    def get_current_step(instance):
        steps = instance.step_set.all()
        current = 0
        for step in steps:
            if step.status not in [-1, 0]:
                current += 1
        return current

    @property
    def is_manual_review(self):
        instance = Strategy.objects.first()
        if not instance:
            instance = Strategy.objects.create()
        return instance.is_manual_review

    def get_db_addr(self, user, password, host, port, actiontype):
        pc = prpcrypt()
        password = pc.decrypt(password)
        dbaddr = '--user={}; --password={}; --host={}; --port={}; {};'.format(user, password, host, port, actiontype)
        return dbaddr

    def has_flow(self, instance):
        return instance.is_manual_review == True and instance.env == self.env_prd

    def replace_remark(self, sqlobj):
        username = self.request.user.username
        uri = self.request.META['PATH_INFO'].split('/')[-2]
        if username != sqlobj.treater:
            sqlobj.remark +=  '   [' + username + self.action_desc_map.get(uri) + ']'
        if sqlobj.handleable == True:
            steps = sqlobj.step_set.all()
            step_obj_second = steps[1]
            if not (self.request.user == step_obj_second.user and uri == 'reject'):
                step_obj = steps[0]
                step_obj.user = self.request.user
                step_obj.save()
        sqlobj.save()

    def check_execute_sql(self, db_id, sql_content):
        dbobj = Dbconf.objects.get(id = db_id)
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)
        sql_review = Inception(sql_content, dbobj.name).inception_handle(db_addr)
        result, status = sql_review.get('result'), sql_review.get('status')
        if status == -1 or len(result) == 1:
            raise ParseError({self.connect_error: result})
        success_sqls = []
        exception_sqls = []
        for sql_result in result:
            error_message = sql_result[4]
            if error_message == 'None' or re.findall('Warning', error_message):
                success_sqls.append(sql_result)
            else:
                exception_sqls.append(error_message)
        if exception_sqls and self.action_type == '--enable-check':
            raise ParseError({self.exception_sqls: exception_sqls})
        return (success_sqls, exception_sqls, json.dumps(result))

    def mail(self, sqlobj, mailtype):
        if sqlobj.env == self.env_prd:
            username = self.request.user.username
            treater = sqlobj.treater
            commiter = sqlobj.commiter
            mailto_users = [treater, commiter]
            mailto_users = list(set(mailto_users))
            mailto_list = [u.email for u in User.objects.filter(username__in = mailto_users)]
            send_mail.delay(mailto_list, username, sqlobj.id, sqlobj.remark, mailtype, sqlobj.sql_content, sqlobj.db.name)
