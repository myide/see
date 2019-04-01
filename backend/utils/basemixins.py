# -*- coding: utf-8 -*-
from utils.dbcrypt import prpcrypt

class HttpMixin(object):

    def get_urls_action(self, request):
        return request.META['PATH_INFO'].split('/')[-2]

class AppellationMixin(object):
    dev = 'developer'
    admin = 'admin'
    dev_spm = 'developer_supremo'
    dev_mng = 'developer_manager'
    env_test = 'test'
    env_prd = 'prd'
    urn_execute = 'execute'
    urn_reject = 'reject'
    urn_approve = 'approve'
    urn_disapprove = 'disapprove'
    urn_rollback = 'rollback'
    urn_cron = 'cron'
    urn_database_order_approve = 'database_order_approve'
    urn_database_order_disapprove = 'database_order_disapprove'
    urn_database_order_reject = 'database_order_reject'
    db_order_apply = 'db_order_apply'
    db_order_approve = 'db_order_approve'
    db_order_disapprove = 'db_order_disapprove'
    db_order_reject = 'db_order_reject'
    name_mail_inception = 'mail_inception'
    name_mail_db_order = 'mail_db_order'

    action_desc_map = {
        'select': ' 代执行',
        'execute': ' 代执行',
        'reject': ' 代放弃',
        'rollback': ' 代回滚',
        'approve':' 代审批通过',
        'disapprove': ' 代审批驳回',
    }

    env_desc_map = {
        env_test: '测试',
        env_prd: '生产'
    }

    reject_steps = {
        dev: 0,
        dev_mng: 1,
        dev_spm: 2
    }

class PromptMixin(object):
    connect_error = 'MySQL连接异常 '
    forbidden_words = '禁用关键字 '
    exception_sql_list = 'SQL语法错误 '
    not_exists_group = '用户的组不存在 '
    executed = 'SQL已执行过'
    approve_warning = '无法重复审批'
    reject_warning = '该工单当前的流转状态不在您这里，无法放弃'
    require_handleable = '该工单未审批通过，无法操作'
    require_different = '执行人和审批人相同，无法操作'
    require_same = '您不是该工单的审批人，无法审批'
    type_warning = 'SELECT语句无法回滚'
    old_password_warning = '旧密码错误'
    new_rep_password_warning = '重复密码错误'
    not_exists_target_db = '目标数据库不存在'
    not_rollback_able = '此类型的SQL不可被回滚'
    get_rollback_fail = '回滚失败(回滚语句未生成)'
    personal_variable_error = '请选择集群和目标数据库'
    get_content_fail = '文件内容为空，无法下载'
    sql_count_exceed = 'SQL条数({}), 已超出限制({})'
    rules_warning = '请先浏览 流程设置 页面'
    select_count_warning = '无法查询多条语句'
    action_status_warning_execute = '无法重复执行'
    action_status_warning_reject = '无法重复放弃'
    action_status_warning_approve = '无法重复审批'
    action_status_warning_rollback = '无法重复回滚'
    action_status_warning_cron = '此状态无法设置定时'
    action_status_warning_database_order_manage = '此状态无法继续审核'
    action_status_warning_database_order_reject = '此状态无法继续放弃'
    invalid_date_warning = '错误的日期格式({})'
    task_locked = '该任务已锁定(工单ID:{})'
    not_exists_admin_mail = '请先设置 管理员组收件人'
    not_edit_status = '此状态无法修改工单'
    permission_warning = '数据库 {} 无权限'
    permission_leader = '无权限：您不是用户 {} 的工单核准人'
    permission_group = '无权限：用户 {} 和您不同组'

class SetEncryptMixin(object):
    parameter = 'password'

    def create(self, validated_data):
        password = validated_data.get(self.parameter)
        validated_data[self.parameter] = prpcrypt.encrypt(password)
        return super(SetEncryptMixin, self).create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get(self.parameter)
        if password != instance.password:
            validated_data[self.parameter] = prpcrypt.encrypt(password)
        return super(SetEncryptMixin, self).update(instance, validated_data)
