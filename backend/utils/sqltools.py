# -*- coding: utf-8 -*-
import configparser
import subprocess
import pymysql
from rest_framework.exceptions import ParseError
from django.conf import settings
from .dbcrypt import prpcrypt
from sqlmng.models import InceptionConnection

class Inception(object):

    def __init__(self, sql, db_name = ''):
        self.sql = sql
        self.db_name = db_name

    @property
    def get_inception_conn(self):
        instance = InceptionConnection.objects.first()
        return {
            'host':instance.host,
            'port':int(instance.port)
        }

    @property
    def get_inception_backup(self):
        conf = configparser.ConfigParser()
        file_path = settings.INCEPTION_SETTINGS.get('file_path')
        conf.read(file_path)
        return {
            'host': conf.get('inception', 'inception_remote_backup_host'),
            'port': int(conf.get('inception', 'inception_remote_backup_port')),
            'user': conf.get('inception', 'inception_remote_system_user'),
            'passwd': conf.get('inception', 'inception_remote_system_password')
        }

    def inception_handle(self, dbaddr):
        status = 0
        sql = '/* {} */\
            inception_magic_start;\
            use `{}`; {} inception_magic_commit;'.format(dbaddr, self.db_name, self.sql)
        try:
            conn = pymysql.connect(user='', passwd='', db='', use_unicode=True, charset="utf8", **self.get_inception_conn)
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            conn.close()
        except pymysql.Error as e:
            status = -1
            result = "Mysql Error {}: {}".format(e.args[0], e.args[1])
        return {'result': result, 'status': status}

    def manual(self):  # 查询回滚库/表
        try:
            conn = pymysql.connect(db=self.db_name, charset='utf8', **self.get_inception_backup)
            cur = conn.cursor()
            cur.execute(self.sql)
            conn.close()
        except Exception:
            return []
        return cur.fetchall()

    def get_back_table(self):
        return self.manual()[0][0]

    def get_back_sql(self):
        per_rollback = self.manual()
        back_sql = ''
        for i in per_rollback:
            back_sql += i[0]
        return back_sql

    def get_index_list(self):
        data = self.manual()[3:]
        return [index_info[0] for index_info in data]

class SoarParams(object):
    allow_online = '-allow-online-as-test'
    only_syntax = '-only-syntax-check'
    fingerprint = '-report-type=fingerprint'
    pretty = '-report-type=pretty'

class HandleConn(object):

    def __init__(self):
        self.conn_conf = {
            'use_unicode': True,
            'charset': 'utf8'
        }

    @classmethod
    def convert_params(cls, params):
        params['port'] = int(params.get('port', 0))
        return params

    def main(self, params, sql, select=False):   # 查询目标库/表结构
        params.update(self.conn_conf)
        try:
            params = self.convert_params(params)
            conn = pymysql.connect(**params)
            cur = conn.cursor()
            cur.execute(sql)
            conn.close()
        except Exception as e:
            if select:
                return 2, [e]
            raise ParseError(e)
        return 0, cur.fetchall()

class AutoQuery(HandleConn):

    def get_databases(self, params):
        sql = 'SHOW DATABASES;'
        return self.main(params, sql)[1]

    def conn_database(self, params):
        sql = 'USE {}'.format(params.get('db'))
        return self.main(params, sql)

class SqlQuery(HandleConn):

    def __init__(self, instance):
        super(SqlQuery, self).__init__()
        self.db = instance
        self.password = prpcrypt.decrypt(self.db.password)
        self.soar_cli = settings.OPTIMIZE_SETTINGS.get('soar_cli')
        self.sqladvisor_cli = settings.OPTIMIZE_SETTINGS.get('sqladvisor_cli')
        self.params = {
            'host': self.db.host,
            'port': self.db.port,
            'user': self.db.user,
            'passwd': self.password,
            'db': self.db.name
        }

    def convert_sql(self, sql):
        return sql.replace('"', '\'')

    def get_tables(self):
        sql = 'SHOW TABLES;'.format(self.db.name)
        data = self.main(self.params, sql)[1]
        tables = [i[0] for i in data]
        return tables

    def get_select_result(self, sql):
        data = self.main(self.params, sql, select=True)
        return data

    def get_table_info(self, table_name):
        sql = 'SHOW CREATE TABLE {}'.format(table_name)
        table_info = self.main(self.params, sql)[1][0][1]
        return table_info

    def get_user_drop_priv(self):
        sql = "SELECT Drop_priv FROM mysql.user WHERE User='{}' AND Host='{}'".format(self.db.user, 'localhost')
        try:
            priv = self.main(self.params, sql)[1][0][0]
        except Exception:
            priv = 'N'
        return '-online-dsn' if priv == 'N' else '-test-dsn'

    def cmd_res(self, cmd):
        data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return data.stdout.read().decode('utf-8')

    def sql_advisor(self, sql):
        cmd = '{} -h {} -P {} -u {} -p "{}" -d {} -q "{};" -v 1'.format(self.sqladvisor_cli, self.db.host, self.db.port, self.db.user, self.password, self.db.name, self.convert_sql(sql))
        return self.cmd_res(cmd)

    def sql_soar(self, sql, soar_type):
        dsn = self.get_user_drop_priv()
        cmd = 'echo "{}" | {} {}="{}:{}@{}:{}/{}" {}'.format(self.convert_sql(sql), self.soar_cli, dsn, self.db.user, self.password, self.db.host, self.db.port, self.db.name, getattr(SoarParams, soar_type))
        return self.cmd_res(cmd)
