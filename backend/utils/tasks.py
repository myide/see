#coding=utf-8
import smtplib
from email.mime.text import MIMEText
from celery import task

smtp_host = "smtp.163.com"  #设置服务器
smtp_port = 25  #SMTP协议默认端口是25
mail_user = "sql_see@163.com"  #用户名
mail_pass = "see123"  #授权码

@task
def send_mail(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname):  #to_list：收件人；sub：主题；content：邮件内容
    to_list.append(mail_user)
    if action_type == '--enable-check':
        title = '提交了 SQL工单-{}'.format(sqlid)
    elif action_type == '--enable-execute':
        title = '已执行 SQL工单-{}'.format(sqlid)
    sqlhtml = ''
    for s in sqlcontent[0:1024].split(';'):
        if s:
            sqlhtml = sqlhtml + '<div>' + s + ';' + '</div>'
    contenthtml = "<span style='margin-right:20px'>{} {}</span> <a href='http://sql.aaa.com/inceptionsql/{}'>【查看详情】</a> <p>备注：{}</p> <p>数据库（生产环境）：{} </p>".format(personnel, title, sqlid, note, dbname)
    if len(sqlcontent) > 1024:
        sqlhtml = sqlhtml + '<div>' + '略... ...（内容比较多，可查看详情）'  + '</div>'
    msg = MIMEText(contenthtml + sqlhtml, _subtype='html', _charset='utf-8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = '{} {} [{}]'.format(personnel, title, note)    #设置主题
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP(smtp_host, smtp_port)
        s.login(mail_user, mail_pass)  #登陆服务器
        s.sendmail(mail_user, to_list, msg.as_string())  #发送邮件
        s.quit()
        return True
    except Exception as e:
        print(e)
        return False
