#coding=utf-8
from celery import task
import smtplib
from email.mime.text import MIMEText

mail_host = "email.aaa.com"  #设置服务器
mail_user = "user1"    #用户名
mail_pass = "passwd1"   #密码
mail_postfix = "aaa.com"  #发件箱的后缀

@task
def send_mail(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname):  #to_list：收件人；sub：主题；content：邮件内容
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
    me = "<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(contenthtml + sqlhtml, _subtype='html', _charset='utf-8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = '{} {} [{}]'.format(personnel, title, note)    #设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host, 587)  #连接smtp服务器
        s.starttls()
        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception as e:
        return False

