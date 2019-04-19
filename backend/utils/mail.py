# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from django.conf import settings

class Mail(object):

    locals().update(settings.MAIL)

    @classmethod
    def get_status(cls, status):
        status_map = {
            -3: '回滚成功',
            0: '执行成功',
            2: '任务异常'
        }
        return status_map.get(status, None)

    @classmethod
    def send(cls, kwargs):  # mail_list：收件人；sub：主题；content：邮件内容
        source_app = kwargs.get('source_app')
        func = getattr(cls, source_app)
        title, content_html, sql_html, mail_list, personnel, remark = func(kwargs)
        msg = MIMEText(content_html + sql_html, _subtype='html', _charset='utf-8')  # 创建一个实例，这里设置为html格式邮件
        msg['Subject'] = '{} {} {}'.format(personnel, title, remark)  # 设置主题
        msg['From'] = cls.mail_user
        msg['To'] = ";".join(mail_list)
        try:
            server = smtplib.SMTP_SSL(cls.smtp_host, cls.smtp_port, timeout=cls.timeout)
        except Exception as e:
            print(e)
            server = smtplib.SMTP(cls.smtp_host, cls.smtp_port, timeout=cls.timeout)
            server.starttls()
        try:
            server.login(cls.mail_user, cls.mail_pass)  # 登陆服务器
            server.sendmail(cls.mail_user, mail_list, msg.as_string())  # 发送邮件
            server.quit()
        except Exception as e:
            print(e)

    @classmethod
    def mail_inception(cls, kwargs):
        mail_list = kwargs.get('mail_list')
        personnel = kwargs.get('personnel')
        instance_id = kwargs.get('instance_id')
        remark = kwargs.get('remark')
        sql_content = kwargs.get('sql_content')
        db_name = kwargs.get('db_name')
        status = kwargs.get('status')
        desc_cn = kwargs.get('desc_cn')
        title = '{} SQL工单-{}'.format(desc_cn, instance_id)
        sql_html = ''
        for s in sql_content[0:1024].split(';'):
            if s:
                sql_html = sql_html + '<div>' + s + ';' + '</div>'
        status_tag = cls.get_status(status)
        status_html = '<p>工单状态：{}</p>'.format(status_tag) if status_tag else ''
        content_html = "<span style='margin-right:20px'>{} {}</span> <a href='{}/inceptionsql/{}'>【查看详情】</a> <p>备注：{}</p> <p>数据库（生产环境）：{} </p>".format(personnel, title, cls.see_addr, instance_id, remark, db_name)
        content_html += status_html
        if len(sql_content) > 1024:
            sql_html = sql_html + '<div>' + '略... ...（内容较多，可查看详情）' + '</div>'
        return title, content_html, sql_html, mail_list, personnel, remark

    @classmethod
    def mail_db_order(cls, kwargs):
        mail_list = kwargs.get('mail_list')
        personnel = kwargs.get('personnel')
        instance_id = kwargs.get('instance_id')
        remark = kwargs.get('remark')
        desc_cn = kwargs.get('desc_cn')
        data_dict = kwargs.get('data_dict')
        title = '{}-{}'.format(desc_cn, instance_id)
        content_html = '<div><p>[配置信息]</p><p>环境：{}</p> <p>主机：{}</p> <p>端口：{}</p> <p>数据库列表：{}</p> <p>备注：{}</p></div>'.format(
            data_dict.get('env'),
            data_dict.get('db_host'),
            data_dict.get('db_port'),
            data_dict.get('db_list'),
            data_dict.get('remark')
        )
        return title, content_html, '', mail_list, personnel, remark
