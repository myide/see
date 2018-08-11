#coding=utf-8

import pymysql

def table_structure(dbaddr, dbname, sqlcontent):
    status = 0
    sql = '/* {} */\
      inception_magic_start;\
      use {}; {} inception_magic_commit;'.format(dbaddr, dbname, sqlcontent)
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
    return {'result':result, 'status':status}

def get_rollback(sql, dbname=''):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '123456', db = dbname, charset = 'utf8')  # 连接回滚库
    conn.autocommit(True)
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

