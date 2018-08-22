#coding=utf-8

import pymysql

class Inception(object):

    def __init__(self, sql, dbname = ''):
        self.sql = sql
        self.dbname = dbname

    def inception_handle(self, dbaddr):
        status = 0
        sql = '/* {} */\
          inception_magic_start;\
          use {}; {} inception_magic_commit;'.format(dbaddr, self.dbname, self.sql)
        try:
            conn = pymysql.connect(host='127.0.0.1', user='root', passwd='', port=6669, db='', use_unicode=True, charset="utf8")  # 连接inception
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
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db=self.dbname, charset='utf8')  # 连接回滚库
        conn.autocommit(True)
        cur = conn.cursor()
        cur.execute(self.sql)
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
