#coding=utf8
import re
import time
import json
import subprocess
import configparser
from rest_framework.exceptions import ParseError
from django.conf import settings
from utils.tasks import send_mail
from utils.basemixins import AppellationMixins, PromptMixins
from utils.dbcrypt import prpcrypt
from utils.basecomponent import DateEncoder
from utils.baseviews import ReturnFormatMixin as res
from utils.sqltools import Inception, SqlQuery
from utils.lock import RedisLock
from utils.wrappers import timer
from .data import inception_conn
from .models import *

class FixedDataMixins(object):

    def get_queryset(self):
        model = self.serializer_class.Meta.model
        objects = model.objects
        queryset = objects.all()
        if queryset.count() != len(self.source_data):
            queryset.delete()
            datas = [model(**data) for data in self.source_data]
            objects.bulk_create(datas)
            queryset = objects.all()
        return queryset

class ChangeSpecialCharacterMixins(object):

    special_character_list = ['*']
    transference_character = '\\'

    def convert(self, forbidden_words):
        forbidden_words_list = forbidden_words.split()
        forbidden_list = []
        for word in forbidden_words_list:
            if word:
                if word in self.special_character_list:
                    word = '{}{}'.format(self.transference_character, word)
                forbidden_list.append(word)
        return forbidden_list

    def reverse(self, forbidden_list):
        forbiddens = []
        for word in forbidden_list:
            if self.transference_character in word:
                word = word.replace(self.transference_character, '')
            forbiddens.append(word)
        if len(forbiddens) == 1:
            return forbiddens[0]
        return forbiddens

class InceptionConn(object):

    error_tag = 'error'
    model = InceptionConnection

    def get_cmd(self, sub_cmd):
        conn = self.get_inception_conn()
        return '{} -e "{}" '.format(conn, sub_cmd)

    def get_inception_conn(self):
        instance = self.model.objects.first()
        obj = instance or self.model.objects.get_or_create(**inception_conn[0])[0]
        return 'mysql -h{} -P{}'.format(obj.host, obj.port)

    def get_mysql_conn(self, params):
        return 'mysql -h{} -P{} -u{} -p{} -e "use {}" '.format(
            params.get('host'),
            params.get('port'),
            params.get('user'),
            params.get('password'),
            params.get('db')
        )

class CheckConn(InceptionConn):

    conf = configparser.ConfigParser()
    file_path = settings.INCEPTION_SETTINGS.get('file_path')

    def check(self, request):
        ret = res.get_ret()
        request_data = request.data
        check_type = request_data.get('check_type')
        if check_type == 'inception_conn':
            sub_cmd = "inception get variables"
            cmd = self.get_cmd(sub_cmd)
        else:
            params = {}
            if check_type == 'inception_backup':
                self.conf.read(self.file_path)
                password = self.conf.get('inception', 'inception_remote_system_password')
                params = request_data
                params['password'] = password
                params['db'] = 'inception'
            elif check_type == 'update_target_db':
                db_id = request_data.get('id')
                instance = Dbconf.objects.get(id=db_id)
                params = {
                    'db': instance.name,
                    'host': instance.host,
                    'port': instance.port,
                    'user': instance.user,
                    'password': prpcrypt.decrypt(instance.password)
                }
            elif check_type == 'create_target_db':
                params = request_data
            cmd = self.get_mysql_conn(params)
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = popen.stdout.readlines()
        last_item = lines[-1].decode('gbk') if len(lines) > 0 else ''
        if self.error_tag in last_item.lower():
            ret['status'] = -1
            ret['data'] = last_item
        return ret

class HandleInceptionSettingsMixins(InceptionConn):
    backup_variables = [
        'inception_remote_backup_host',
        'inception_remote_backup_port',
        'inception_remote_system_user',
        'inception_remote_system_password'
    ]

    def get_inception_backup(self):
        return {variable:self.get_status(variable) for variable in self.backup_variables}

    def get_status(self, variable_name):
        filter_words = [variable_name, '\t', '\n']
        sub_cmd = "inception get variables '{}'".format(variable_name)
        cmd = self.get_cmd(sub_cmd)
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = popen.stdout.readlines()
        if not lines:
            return None
        res = lines[-1].decode('gbk')
        if self.error_tag in res.lower():
            return None
        for word in filter_words:
            res = res.replace(word, '')
        return res

    def set_variable(self, request):
        request_data = request.data
        variable_name = request_data.get('variable_name')
        variable_value = request_data.get('variable_value')
        sub_cmd = "inception set {}={}".format(variable_name, variable_value)
        cmd = self.get_cmd(sub_cmd)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

class ActionMixins(PromptMixins, AppellationMixins):

    type_select_tag = 'select'
    action_type_execute = '--enable-execute'
    action_type_check = '--enable-check'
    success_tag = 'Execute Successfully\nBackup successfully'

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
    def get_urls_action(self):
        return self.request.META['PATH_INFO'].split('/')[-2]

    @property
    def is_manual_review(self):
        instance = Strategy.objects.first()
        if not instance:
            instance = Strategy.objects.create()
        return instance.is_manual_review

    def check_approve_status(self, instance):
        step_instance = instance.workorder.step_set.all()[1]
        if step_instance.status != 0:
            raise ParseError(self.approve_warning)

    def handle_workflow(self, call_type, status, step_number, instance=None):
        instance = instance or self.get_object()
        if self.has_flow(instance):
            if call_type == 1:  # 1 审批类的, 2 执行, 3 放弃
                self.check_approve_status(instance)
                if status == 1:
                    self.save_instance(instance.workorder, True)
            step_instance = instance.workorder.step_set.order_by('id')[step_number]
            self.save_instance(step_instance, status)
            if call_type == 3:  # 放弃工单，需要把当前step以后的step置为终止状态（-1）
                steps = instance.workorder.step_set.all()
                steps_behind = steps.filter(id__gt=step_instance.id)
                for step in steps_behind:
                    self.save_instance(step, -1)

    def get_db_addr(self, user, password, host, port, actiontype):
        password = prpcrypt.decrypt(password)
        dbaddr = '--user={}; --password={}; --host={}; --port={}; {};'.format(user, password, host, port, actiontype)
        return dbaddr

    def has_flow(self, instance):
        return instance.is_manual_review == True and instance.env == self.env_prd

    @classmethod
    def save_instance(cls, instance, status=None):
        if status is not None:
            instance.status = status
        instance.save()

    def check_status(self, instance):
        action = self.get_urls_action
        if action == 'execute' and instance.status not in [-1, 3]:
            raise ParseError(self.action_status_warning_execute)

    def check_lock(self, instance):
        if not RedisLock.locked(instance.id):
            raise ParseError(self.task_locked.format(instance.id))

    def filter_select_type(self, instance):
        type = instance.type
        if type == self.type_select_tag:
            raise ParseError(self.type_warning)

    def check_valid_date(self, cron_time):
        date_format = settings.CELERY_BUSINESS_PARAMS.get('date_format')
        try:
            time.mktime(time.strptime(cron_time, date_format))
        except Exception:
            raise ParseError(self.invalid_date_warning.format(cron_time))

    def filter_date(self, queryset):
        date_range = self.request.GET.get('daterange')
        if date_range:
            return queryset.filter(createtime__range = date_range.split(','))
        return queryset

    def check_rollbackable(self, instance):
        if not instance.rollback_able:
            raise ParseError(self.not_rollback_able)

    def check_execute_sql(self, db_id, sql_content, action_type):
        dbobj = Dbconf.objects.get(id=db_id)
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, action_type)
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
        if exception_sqls and action_type == self.action_type_check:
            raise ParseError({self.exception_sqls: exception_sqls})
        return success_sqls, exception_sqls, json.dumps(result)

    def replace_remark(self, instance, action=None, user=None):
        user = user or self.request.user
        username = user.username
        action = action or self.get_urls_action
        if username != instance.treater:
            instance.remark +=  '   [' + username + self.action_desc_map.get(action) + ']'
        if instance.workorder.status == True:
            steps = instance.workorder.step_set.all()
            step_obj_second = steps[1]
            if user and not (user == step_obj_second.user and action == 'reject'):
                step_obj = steps[0]
                step_obj.user = user
                self.save_instance(step_obj)

    def get_extend_mail_list(self, user):
        mail_list_extend = user.mail_list_extend
        return mail_list_extend.split() if mail_list_extend else []

    def mail(self, instance, mail_type, personnel):
        try:
            mail_action = MailActions.objects.get(name=mail_type)
        except Exception:
            return
        if (instance.env == self.env_prd) and mail_action.value:
            commiter = instance.commiter
            treater = instance.treater
            user = User.objects.get(username=commiter)
            admin_mail = user.admin_mail.username if user.admin_mail else None
            mail_users = [ commiter, treater, admin_mail]
            mail_list_extend = self.get_extend_mail_list(user)
            mail_list = [u.email for u in User.objects.filter(username__in = mail_users)]
            mail_list.extend(mail_list_extend)
            mail_list = list(set(mail_list))
            send_mail.delay(mail_list, personnel.username, instance.id, instance.remark, mail_type, instance.sql_content, instance.db.name)

class Handle(ActionMixins):

    @timer
    def select(self, instance):
        sql_query = SqlQuery(instance.db)
        data = sql_query.main(instance.sql_content)
        affected_rows = len(data)
        instance.handle_result_execute = json.dumps([str(row) for row in data], cls=DateEncoder)
        instance.status = 0
        return instance, affected_rows

    @timer
    def execute(self, instance):
        affected_rows = 0
        opids = []
        rollback_able = False
        instance.status = 0
        success_sqls, exception_sqls, handle_result_execute = self.check_execute_sql(instance.db.id, instance.sql_content, self.action_type_execute)
        for success_sql in success_sqls:
            instance.rollback_db = success_sql[8]
            affected_rows += success_sql[6]
            if re.findall(self.success_tag, success_sql[3]):
                rollback_able = True
                opids.append(success_sql[7].replace("'", ""))
        if exception_sqls:
            instance.status = 2
            instance.execute_errors = exception_sqls
        instance.rollback_opid = opids
        instance.rollback_able = rollback_able
        instance.handle_result_execute = handle_result_execute
        return instance, affected_rows

    @timer
    def rollback(self, instance):
        self.filter_select_type(instance)
        self.check_rollbackable(instance)
        dbobj = instance.db
        rollback_opid_list = instance.rollback_opid
        rollback_db = instance.rollback_db
        back_sqls = ''
        for opid in eval(rollback_opid_list):
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = Inception(back_source, rollback_db).get_back_table()
            statement_sql = 'select rollback_statement from {} where opid_time = "{}" '.format(back_table, opid)
            rollback_statement = Inception(statement_sql, rollback_db).get_back_sql()
            if not rollback_statement:
                raise ParseError(self.get_rollback_fail)
            back_sqls += rollback_statement
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type_execute)
        execute_results = Inception(back_sqls, dbobj.name).inception_handle(db_addr).get('result')
        status = -3
        for result in execute_results:
            if result[4] != 'None':
                status = 2
                break
        instance.status = status
        instance.handle_result_rollback = json.dumps(execute_results)
        return instance, instance.affected_rows
