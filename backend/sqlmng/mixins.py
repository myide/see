#coding=utf8
from rest_framework.exceptions import ParseError
from utils.tasks import send_mail
from utils.basemixins import AppellationMixins
from utils.dbcrypt import prpcrypt
from utils.sqltools import Inception
from .models import *
import re
import json

class ActionMxins(AppellationMixins, object):

    type_select_tag = 'select'
    action_type_execute = '--enable-execute'
    action_type_check = '--enable-check'

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
        steps = instance.workorder.step_set.all()
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
        if username != sqlobj.treater:  # 如果是dba或总监代执行的
            sqlobj.remark +=  '   [' + username + self.action_desc_map.get(uri) + ']'
        if sqlobj.workorder.status == True:  # 改step第三人名字 (审批通过了，说明 此工单是有流程的.且到了step 2)
            # 排除step 2的人, 做reject 的情形:
            steps = sqlobj.workorder.step_set.all()
            step_obj_second = steps[1]
            if not (self.request.user == step_obj_second.user and uri == 'reject'):
                step_obj = steps[0]
                step_obj.user = self.request.user
                step_obj.save()
        sqlobj.save()

    def check_execute_sql(self, db_id, sql_content, action_type):
        dbobj = Dbconf.objects.get(id = db_id)
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, action_type)  # 根据数据库名 匹配其地址信息，"--check=1;" 只审核
        sql_review = Inception(sql_content, dbobj.name).inception_handle(db_addr)  # 审核
        result, status = sql_review.get('result'), sql_review.get('status')
        # 判断检测错误，有则返回
        if status == -1 or len(result) == 1:  # 兼容2种版本的抛错
            raise ParseError({self.connect_error: result})
        success_sqls = []
        exception_sqls = []
        for sql_result in result:
            error_message = sql_result[4]
            if error_message == 'None' or re.findall('Warning', error_message):
                success_sqls.append(sql_result)
            else:
                exception_sqls.append(error_message)
        if exception_sqls and action_type == self.action_type_check:
            raise ParseError({self.exception_sqls: exception_sqls})
        return (success_sqls, exception_sqls, json.dumps(result))

    def mail(self, sqlobj, mailtype):
        if sqlobj.env == self.env_prd:  # 线上环境，发邮件提醒
            username = self.request.user.username
            treater = sqlobj.treater  # 执行人
            commiter = sqlobj.commiter  # 提交人
            mailto_users = [treater, commiter]
            mailto_users = list(set(mailto_users))  # 去重（避免提交人和执行人是同一人，每次收2封邮件的bug）
            mailto_list = [u.email for u in User.objects.filter(username__in = mailto_users)]
            # 发送邮件，并判断结果
            send_mail.delay(mailto_list, username, sqlobj.id, sqlobj.remark, mailtype, sqlobj.sql_content, sqlobj.db.name)
