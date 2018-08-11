#coding=utf-8
from celery import task
import smtplib
from email.mime.text import MIMEText

mail_host = "email.aaa.com"  #设置服务器
mail_user = "user1"    #用户名
mail_pass = "passwd1"   #密码
mail_postfix = "aaa.com"  #发件箱的后缀

@task
def send_mail(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname):
    if action_type == '--enable-check':
        title = '提交了 SQL-{}'.format(sqlid)
    elif action_type == '--enable-execute':
        title = '已执行 SQL-{}'.format(sqlid)
    sqlhtml = ''
    for s in sqlcontent[0:1024].split(';'):
        if s:
            sqlhtml = sqlhtml + '<div>' + s + ';' + '</div>'
    contenthtml = "<span style='margin-right:20px'>{} {}</span> <a href='http://sql.aaa.com/sql/{}'>【查看详情】</a> <p>备注：{}</p> <p>数据库（线上环境）：{} </p>".format(personnel, title, sqlid, note, dbname)
    if len(sqlcontent) > 1024:
        sqlhtml = sqlhtml + '<div>' + '略... ...（内容比较多，可查看详情）'  + '</div>'
    #me = "hello"+"<"+mail_user+"@"+mail_postfix+">"
    me = "<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(contenthtml + sqlhtml, _subtype='html', _charset='utf-8')
    msg['Subject'] = '{} {} [{}]'.format(personnel, title, note)
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host, 587)
        s.starttls()
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception as e:
        return False

