#coding=utf-8
import configparser
import subprocess
import pymysql
from rest_framework.exceptions import ParseError
from django.conf import settings
from .dbcrypt import prpcrypt
from sqlmng.models import InceptionConnection

class Inception(object):

    def __init__(self, sql, dbname = ''):
        self.sql = sql
        self.dbname = dbname

    @property
    def get_inception_conn(self):
        instance = InceptionConnection.objects.all()[0]
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
          use {}; {} inception_magic_commit;'.format(dbaddr, self.dbname, self.sql)
        try:
            conn = pymysql.connect(user='', passwd='', db='', use_unicode=True, charset="utf8", **self.get_inception_conn)
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            conn.close()
        except pymysql.Error as e:
            status = -1
            result = "Mysql Error {}: {}".format(e.args[0], e.args[1])
        return {'result': result, 'status': status}

    def manual(self):
        conn = pymysql.connect(db=self.dbname, charset='utf8', **self.get_inception_backup)
        conn.autocommit(True)
        cur = conn.cursor()
        try:
            cur.execute(self.sql)
        except pymysql.err.ProgrammingError:
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
        res = self.manual()[3:]
        return [index_info[0] for index_info in res]

class SqlQuery(object):
    def __init__(self, instance):
        self.instance = instance
        self.pc = prpcrypt()

    def decrypt_password(self, password):
        return self.pc.decrypt(password)

    def main(self, sql):
        db = self.instance
        password = self.decrypt_password(db.password)
        try:
            conn = pymysql.connect(host=db.host, port=int(db.port), user=db.user, passwd=password, db=db.name, charset='utf8')
            conn.autocommit(True)
            cur = conn.cursor()
            cur.execute(sql)
        except Exception as e:
            raise ParseError(e)
        return cur.fetchall()

    def get_tables(self):
        sql = 'show tables;'.format(self.instance.name)
        res = self.main(sql)
        tables = [i[0] for i in res]
        return tables

    def get_table_info(self, table_name):
        sql = 'SHOW CREATE TABLE {}'.format(table_name)
        table_info = self.main(sql)[0][1]
        return table_info

    def sql_advisor(self, sql):
        db = self.instance
        password = self.decrypt_password(db.password)
        cmd_path = '/usr/bin/sqladvisor'
        cmd = "{} -h {} -P {}  -u {} -p '{}' -d {} -q '{};' -v 1".format(cmd_path, db.host, db.port, db.user, password, db.name, sql)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return res.stdout.read()
