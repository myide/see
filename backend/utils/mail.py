#coding=utf-8
import smtplib
from email.mime.text import MIMEText
from django.conf import settings

class Mail(object):
    '''
        修改邮件配置: sqlweb/settings.py
    '''
    locals().update(settings.MAIL)

    @classmethod
    def get_desc(cls, action_type):
        desc_map = {
            '--enable-check': '提交',
            '--enable-execute': '执行',
            'approve': '审批',
            'disapprove': '驳回',
            'reject': '放弃',
            'rollback': '回滚'
        }
        return desc_map.get(action_type)

    @classmethod
    def get_mail_template(cls, to_list, action_type, sqlid, sqlcontent, personnel, note, dbname):
        to_list.append(cls.mail_user)
        title = '{} SQL工单-{}'.format(cls.get_desc(action_type), sqlid)
        sql_html = ''
        for s in sqlcontent[0:1024].split(';'):
            if s:
                sql_html = sql_html + '<div>' + s + ';' + '</div>'
        content_html = "<span style='margin-right:20px'>{} {}</span> <a href='{}/inceptionsql/{}'>【查看详情】</a> <p>备注：{}</p> <p>数据库（生产环境）：{} </p>".format(personnel, title, cls.see_addr, sqlid, note, dbname)
        if len(sqlcontent) > 1024:
            sql_html = sql_html + '<div>' + '略... ...（内容较多，可查看详情）' + '</div>'
        return title, content_html, sql_html, to_list

    @classmethod
    def send(cls, to_list, personnel, sqlid, note, action_type, sqlcontent, dbname):
        title, content_html, sql_html, to_list = cls.get_mail_template(to_list, action_type, sqlid, sqlcontent, personnel, note, dbname)
        msg = MIMEText(content_html + sql_html, _subtype='html', _charset='utf-8')
        msg['Subject'] = '{} {} {}'.format(personnel, title, note)
        msg['From'] = cls.mail_user
        msg['To'] = ";".join(to_list)
        try:
            smtp = smtplib.SMTP(cls.smtp_host, cls.smtp_port)
            smtp.starttls()
            smtp.login(cls.mail_user, cls.mail_pass)
            smtp.sendmail(cls.mail_user, to_list, msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            print(e)
            return False
