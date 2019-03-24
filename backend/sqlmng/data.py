# -*- coding: utf-8 -*-

auth_rules = [
	{
		'is_manual_review':True,
		'role':'developer',
		'env':'prd',
		'reject':True,
		'cron':False,
		'execute':False,
		'rollback':False,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':True,
		'role':'developer_manager',
		'env':'prd',
		'reject':True,
		'cron': False,
		'execute':False,
		'rollback':False,
		'approve':True,
		'disapprove':True
	},
	{
		'is_manual_review':True,
		'role':'developer_supremo',
		'env':'prd',
		'reject':True,
		'cron': False,
		'execute':False,
		'rollback':False,
		'approve':True,
		'disapprove':True
	},
	{
		'is_manual_review':True,
		'role':'admin',
		'env':'prd',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':True,
		'disapprove':True
	},

	{
		'is_manual_review':False,
		'role':'developer',
		'env':'prd',
		'reject':True,
		'cron': False,
		'execute':False,
		'rollback':False,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'developer_manager',
		'env':'prd',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'developer_supremo',
		'env':'prd',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'admin',
		'env':'prd',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},

	{
		'is_manual_review':True,
		'role':'developer',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':True,
		'role':'developer_manager',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':True,
		'role':'developer_supremo',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':True,
		'role':'admin',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},

	{
		'is_manual_review':False,
		'role':'developer',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'developer_manager',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'developer_supremo',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},
	{
		'is_manual_review':False,
		'role':'admin',
		'env':'test',
		'reject':True,
		'cron': True,
		'execute':True,
		'rollback':True,
		'approve':False,
		'disapprove':False
	},

]

step_rules = {
	'developer':
        {
            'commiter_true': [1],
            'commiter_false': [1]
        },
	'developer_manager':
        {
            'commiter_true': [1, 2],
            'commiter_false': [1, 2]
        },
	'developer_supremo':
        {
            'commiter_true': [1, 2],
            'commiter_false': [2, 3]
        },
	'admin':
        {
            'commiter_true': [1, 2],
            'commiter_false': [2, 3]
        }
}

variables = [
    {
        'name':'inception_check_insert_field',
        'param':'ON/OFF',
        'default':'ON',
        'instructions':'是不是要检查插入语句中的列链表的存在性'
    },
    {
        'name': 'inception_check_dml_where',
        'param': 'ON/OFF',
        'default': 'ON',
        'instructions': '在DML语句中没有WHERE条件时，是不是要报错'
    },
	{
		'name': 'inception_check_dml_limit',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '在DML语句中使用了LIMIT时，是不是要报错'
	},
	{
		'name': 'inception_check_dml_orderby',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '在DML语句中使用了Order By时，是不是要报错'
	},
	{
		'name': 'inception_enable_select_star',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': 'Select*时是不是要报错'
	},
	{
		'name': 'inception_enable_orderby_rand',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': 'order by rand时是不是报错'
	},
	{
		'name': 'inception_enable_nullable',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '创建或者新增列时如果列为NULL，是不是报错'
	},
	{
		'name': 'inception_enable_foreign_key',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '是不是支持外键'
	},
	{
		'name': 'inception_enable_not_innodb',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '建表指定的存储引擎不为Innodb，不报错'
	},
	{
		'name': 'inception_check_table_comment',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '建表时，表没有注释时报错'
	},
	{
		'name': 'inception_check_column_comment',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '建表时，列没有注释时报错'
	},
	{
		'name': 'inception_check_primary_key',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '建表时，如果没有主键，则报错'
	},
	{
		'name': 'inception_enable_partition_table',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '是不是支持分区表'
	},
	{
		'name': 'inception_enable_enum_set_bit',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '是不是支持enum,set,bit数据类型'
	},
	{
		'name': 'inception_check_index_prefix',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '是不是要检查索引名字前缀为"idx_"，检查唯一索引前缀是不是"uniq_"'
	},
	{
		'name': 'inception_enable_autoincrement_unsigned',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '自增列是不是要为无符号型'
	},
	{
		'name': 'inception_check_autoincrement_init_value',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '当建表时自增列的值指定的不为1，则报错'
	},
	{
		'name': 'inception_check_autoincrement_datatype',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '当建表时自增列的类型不为int或者bigint时报错'
	},
	{
		'name': 'inception_check_timestamp_default',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '建表时，如果没有为timestamp类型指定默认值，则报错'
	},
	{
		'name': 'inception_enable_column_charset',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '允许列自己设置字符集'
	},
	{
		'name': 'inception_check_autoincrement_name',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '建表时，如果指定的自增列的名字不为ID，则报错，说明是有意义的，给提示'
	},
	{
		'name': 'inception_merge_alter_table',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '在多个改同一个表的语句出现是，报错，提示合成一个'
	},
	{
		'name': 'inception_check_column_default_value',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '检查在建表、修改列、新增列时，新的列属性是不是要有默认值'
	},
	{
		'name': 'inception_enable_blob_type',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '检查是不是支持BLOB字段，包括建表、修改列、新增列操作'
	},
	{
		'name': 'inception_enable_identifer_keyword',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '检查在SQL语句中，是不是有标识符被写成MySQL的关键字，默认值为报警。'
	},
	{
		'name': 'auto_commit',
		'param': 'ON/OFF',
		'default': 'OFF',
		'instructions': '这个参数的作用是为了匹配Python客户端每次自动设置auto_commit=0的，如果取消则会报错，针对Inception本身没有实际意义'
	},
	{
		'name': 'general_log',
		'param': 'ON/OFF',
		'default': 'ON',
		'instructions': '这个参数就是原生的MySQL的参数，用来记录在Inception服务上执行过哪些语句，用来定位一些问题等'
	},

]

mail_actions = [
	{
		'name':'--enable-check',
		'desc_cn':'审核'
	},
	{
		'name': 'execute',
        'desc_cn':'执行'
	},
	{
		'name': 'select',
        'desc_cn':'查询'
	},
	{
		'name': 'approve',
        'desc_cn':'审批通过'
	},
	{
		'name': 'disapprove',
        'desc_cn':'审批驳回'
	},
	{
		'name': 'reject',
        'desc_cn':'放弃'
	},
	{
		'name': 'rollback',
        'desc_cn':'回滚'
	},
	{
		'name': 'db_order_apply',
        'desc_cn':'申请数据库工单'
	},
	{
		'name': 'db_order_approve',
        'desc_cn':'审核数据库工单'
	},
	{
		'name': 'db_order_disapprove',
        'desc_cn':'驳回数据库工单'
	},
	{
		'name': 'db_order_reject',
        'desc_cn':'放弃数据库工单'
	}
]

inception_conn = [
	{
		'host':'127.0.0.1',
		'port':6669
	}
]

sql_settings = [
	{
		'forbidden_words':'',
		'sql_count_limit':1000
	}
]
