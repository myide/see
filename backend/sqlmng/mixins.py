#coding=utf8
import re
import json
import subprocess
import configparser
from rest_framework.exceptions import ParseError
from django.conf import settings
from utils.tasks import send_mail
from utils.basemixins import AppellationMixins
from utils.dbcrypt import prpcrypt
from utils.baseviews import ReturnFormatMixin as res
from utils.sqltools import Inception
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
        return 'mysql -h{} -P{} -u{} -p{} -e "show databases" '.format(
            params.get('host'),
            params.get('port'),
            params.get('user'),
            params.get('password')
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
                request_data['password'] = password
                params = request_data
            elif check_type == 'update_target_db':
                db_id = request_data.get('id')
                instance = Dbconf.objects.get(id=db_id)
                params = {
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
        last_item = lines[-1].decode('gbk')
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

class ActionMixins(AppellationMixins):

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
    def is_manual_review(self):
        instance = Strategy.objects.first()
        if not instance:
            instance = Strategy.objects.create()
        return instance.is_manual_review

    def get_db_addr(self, user, password, host, port, actiontype):
        password = prpcrypt.decrypt(password)
        dbaddr = '--user={}; --password={}; --host={}; --port={}; {};'.format(user, password, host, port, actiontype)
        return dbaddr

    def has_flow(self, instance):
        return instance.is_manual_review == True and instance.env == self.env_prd

    def replace_remark(self, sqlobj):
        username = self.request.user.username
        uri = self.request.META['PATH_INFO'].split('/')[-2]
        if username != sqlobj.treater:
            sqlobj.remark +=  '   [' + username + self.action_desc_map.get(uri) + ']'
        if sqlobj.workorder.status == True:
            steps = sqlobj.workorder.step_set.all()
            step_obj_second = steps[1]
            if not (self.request.user == step_obj_second.user and uri == 'reject'):
                step_obj = steps[0]
                step_obj.user = self.request.user
                step_obj.save()
        sqlobj.save()

    def check_execute_sql(self, db_id, sql_content, action_type):
        dbobj = Dbconf.objects.get(id = db_id)
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
        return (success_sqls, exception_sqls, json.dumps(result))

    def mail(self, sqlobj, mail_type):
        mail_action = MailActions.objects.get(name=mail_type)
        if (sqlobj.env == self.env_prd) and mail_action.value:
            user = self.request.user
            treater = sqlobj.treater
            commiter = sqlobj.commiter
            admin_mail = user.admin_mail
            mailto_users = [treater, commiter, admin_mail]
            mailto_users = list(set(mailto_users))
            mailto_list = [u.email for u in User.objects.filter(username__in = mailto_users)]
            send_mail.delay(mailto_list, user.username, sqlobj.id, sqlobj.remark, mail_type, sqlobj.sql_content, sqlobj.db.name)
