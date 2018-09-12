#coding=utf-8

import subprocess
import pymysql
from rest_framework.exceptions import ParseError
from .dbcrypt import prpcrypt

class Inception(object):

    def __init__(self, sql, dbname = ''):
        self.sql = sql
        self.dbname = dbname
        ### Inception 数据库地址，用户，密码，端口
        self.inception_ipaddr = '127.0.0.1'
        self.user = 'root'
        self.passwd = '123456'
        self.port = 3306

    def inception_handle(self, dbaddr):
        status = 0
        sql = '/* {} */\
          inception_magic_start;\
          use {}; {} inception_magic_commit;'.format(dbaddr, self.dbname, self.sql)
        try:
            conn = pymysql.connect(host=self.inception_ipaddr, user='', passwd='', port=6669, db='', use_unicode=True, charset="utf8")  # 连接inception
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            conn.close()
        except pymysql.Error as e:
            status = -1
            result = "Mysql Error {}: {}".format(e.args[0], e.args[1])
        return {'result': result, 'status': status}

    def manual(self):  # 查询回滚库/表
        conn = pymysql.connect(host=self.inception_ipaddr, port=self.port, user=self.user, passwd=self.passwd, db=self.dbname, charset='utf8')  # 连接SQL备份服务器
        conn.autocommit(True)
        cur = conn.cursor()
        cur.execute(self.sql)
        return cur.fetchall()

    def get_back_table(self):
        return self.manual()[0][0]

    def get_back_sql(self):
        per_rollback = self.manual()
        back_sql = ''  # 回滚语句
        for i in per_rollback:  # 累加
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

    def main(self, sql):  # 查询目标库/表结构
        db = self.instance
        password = self.decrypt_password(db.password)
        try:
            conn = pymysql.connect(host=db.host, port=int(db.port), user=db.user, passwd=password, db=db.name, charset='utf8')  # 连接目标服务器
        except Exception as e:
            raise ParseError(e)
        conn.autocommit(True)
        cur = conn.cursor()
        cur.execute(sql)
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
