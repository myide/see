
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
