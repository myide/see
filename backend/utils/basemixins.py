from utils.dbcrypt import prpcrypt

class AppellationMixins(object):
    dev_spm = 'developer_supremo'
    dev_mng = 'developer_manager'
    dev = 'developer'
    admin = 'admin'
    env_test = 'test'
    env_prd = 'prd'

    action_desc_map = {
        'execute': '代执行',
        'reject': '代放弃',
        'rollback': '代回滚',
        'approve':'代审批通过',
        'disapprove': '代审批驳回',
    }

    reject_steps = {
        dev: 0,
        dev_mng: 1,
        dev_spm: 2
    }

class PromptMixins(object):
    connect_error = 'MySQL连接异常 '
    forbidden_words = '禁用关键字 '
    exception_sqls = 'SQL语法错误 '
    not_exists_group = '用户的组不存在 '
    executed = 'SQL已执行过'
    approve_warning = '此工单无需重复审批'
    reject_warning = '该工单当前的流转状态不在您这里，无法放弃'
    require_handleable = '该工单未审批通过，无法操作'
    require_different = '执行人和审批人相同，无法操作'
    require_same = '您不是该工单的审批人，无法审批'
    type_warning = '回滚类型错误(SELECT)'
    old_password_warning = '旧密码错误'
    new_rep_password_warning = '重复密码错误'
    not_exists_target_db = '目标数据库不存在'
    not_rollback_able = '此类型的SQL不可被回滚'
    get_rollback_fail = '回滚失败(请检查回滚语句是否生成)'
    personal_variable_error = '请选择集群和目标数据库'

class SetEncryptMixins(object):
    parameter = 'password'
    def create(self, validated_data):
        password = validated_data.get(self.parameter)
        validated_data[self.parameter] = prpcrypt.encrypt(password)
        return super(SetEncryptMixins, self).create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get(self.parameter)
        if password != instance.password:
            validated_data[self.parameter] = prpcrypt.encrypt(password)
        return super(SetEncryptMixins, self).update(instance, validated_data)
