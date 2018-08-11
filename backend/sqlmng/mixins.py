#coding=utf8
from rest_framework.exceptions import ParseError
from utils.tasks import send_mail
from utils.basemixins import AppellationMixins
from utils.dbcrypt import prpcrypt
from utils import inception
from .models import *
import re

class PromptMxins(object):
    connect_error = 'MySQL连接异常 '
    forbidden_words = '禁用关键字 '
    exception_sqls = 'SQL语法错误 '
    not_exists_group = '用户的组不存在 '
    executed = 'SQL已执行过'

class ActionMxins(AppellationMixins, object):

    action_desc_map = {
        'execute': '代执行',
        'reject': '代放弃',
        'rollback': '代回滚'
    }

    def get_db_addr(self, user, password, host, port, actiontype):
        pc = prpcrypt()
        password = pc.decrypt(password)
        dbaddr = '--user={}; --password={}; --host={}; --port={}; {};'.format(user, password, host, port, actiontype)
        return dbaddr

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

    def replace_remark(self, sqlobj):
        username = self.request.user.username
        uri = self.request.META['PATH_INFO'].split('/')[-2]
        if username != sqlobj.treater:  # 如果是dba或总监代执行的
            sqlobj.remark +=  '   [' + username + self.action_desc_map.get(uri) + ']'
        sqlobj.save()

    def check_execute_sql(self, db_id, sql_content):
        dbobj = Dbconf.objects.get(id = db_id)
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)  # 根据数据库名 匹配其地址信息，"--check=1;" 只审核
        sql_review = inception.table_structure(db_addr, dbobj.name, sql_content)  # 审核
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
        if exception_sqls and self.action_type == '--enable-check':
            raise ParseError({self.exception_sqls: exception_sqls})
        return (success_sqls, exception_sqls)
