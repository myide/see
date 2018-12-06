#coding=utf8
import re
import json
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.basemixins import PromptMixins
from utils.sqltools import Inception, SqlQuery
from utils.basecomponent import DateEncoder
from sqlmng.mixins import ActionMixins
from sqlmng.permissions import IsHandleAble
from sqlmng.serializers import *
from sqlmng.models import *

class InceptionMainView(PromptMixins, ActionMixins, BaseView):
    '''
        查询：根据登录者身份返回相关的SQL，支持日期/模糊搜索。操作：执行（execute）, 回滚（rollback）,放弃（reject操作）
    '''
    serializer_class = InceptionSerializer
    permission_classes = [IsHandleAble]
    search_fields = ['commiter', 'sql_content', 'env', 'treater', 'remark']

    def filter_date(self, queryset):
        date_range = self.request.GET.get('daterange')
        if date_range:
            return queryset.filter(createtime__range = date_range.split(','))
        return queryset

    def get_queryset(self):
        userobj = self.request.user
        if userobj.is_superuser:
            return self.filter_date(Inceptsql.objects.all())
        query_set = userobj.groups.first().inceptsql_set.all() if userobj.role == self.dev_spm else userobj.inceptsql_set.all()
        return self.filter_date(query_set)

    def check_approve_status(self, instance):
        step_instance = instance.workorder.step_set.all()[1]
        if step_instance.status != 0:
            raise ParseError(self.approve_warning)

    def filter_select_type(self, instance):
        type = instance.type
        if type == self.type_select_tag:
            raise ParseError(self.type_warning)

    def check_rollbackable(self, instance):
        if not instance.rollback_able:
            raise ParseError(self.not_rollback_able)

    def handle_approve(self, call_type, status, step_number):
        instance = self.get_object()
        if self.has_flow(instance):
            if call_type == 1:
                self.check_approve_status(instance)
                if status == 1:
                    instance.workorder.status = True
                    instance.workorder.save()
            step_instance = instance.workorder.step_set.order_by('id')[step_number]
            step_instance.status = status
            step_instance.save()
            if call_type == 3:
                steps = instance.workorder.step_set.all()
                steps_behind = steps.filter(id__gt=step_instance.id)
                for step in steps_behind:
                    step.status = -1
                    step.save()

    @detail_route()
    def execute(self, request, *args, **kwargs):
        ret = res.get_ret()
        instance = self.get_object()
        if instance.status != -1:
            ret = {'status': -2, 'msg':self.executed}
            return Response(ret)
        affected_rows = 0
        instance.status = 0
        if instance.type == self.type_select_tag:
            sql_query = SqlQuery(instance.db)
            data = sql_query.main(instance.sql_content)
            affected_rows = len(data)
            instance.handle_result_execute = json.dumps([list(row) for row in data], cls=DateEncoder)
        else:
            execute_time = 0
            opids = []
            rollback_able = False
            success_sqls, exception_sqls, handle_result_execute = self.check_execute_sql(instance.db.id, instance.sql_content, self.action_type_execute)
            for success_sql in success_sqls:
                instance.rollback_db = success_sql[8]
                affected_rows += success_sql[6]
                execute_time += float(success_sql[9])
                if re.findall(self.success_tag, success_sql[3]):
                    rollback_able = True
                    opids.append(success_sql[7].replace("'", ""))
            if exception_sqls:
                instance.status = 2
                instance.execute_errors = exception_sqls
                ret['status'] = -1
            instance.rollback_opid = opids
            instance.rollback_able = rollback_able
            instance.handle_result_execute = handle_result_execute
            ret['data']['execute_time'] = '%.3f' % execute_time
        instance.exe_affected_rows = affected_rows
        ret['data']['affected_rows'] = affected_rows
        self.replace_remark(instance)
        self.handle_approve(2,1,2)
        self.mail(instance, self.action_type_execute)
        return Response(ret)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 1
        self.replace_remark(instance)
        role_step = self.get_reject_step(instance)
        self.handle_approve(3,3,role_step)
        self.mail(instance, self.reject.__name__)
        return Response(res.get_ret())

    @detail_route()
    def approve(self, request, *args, **kwargs):
        self.handle_approve(1,1,1)
        self.mail(self.get_object(), self.approve.__name__)
        return Response(res.get_ret())

    @detail_route()
    def disapprove(self, request, *args, **kwargs):
        self.handle_approve(1,2,1)
        self.mail(self.get_object(), self.disapprove.__name__)
        return Response(res.get_ret())

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        ret = res.get_ret()
        instance = self.get_object()
        self.filter_select_type(instance)
        self.check_rollbackable(instance)
        dbobj = instance.db
        rollback_opid_list = instance.rollback_opid
        rollback_db = instance.rollback_db
        back_sqls = ''
        for opid in eval(rollback_opid_list):
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = Inception(back_source, rollback_db).get_back_table()
            statement_sql = 'select rollback_statement from {} where opid_time = "{}" '.format(back_table, opid)
            rollback_statement = Inception(statement_sql, rollback_db).get_back_sql()
            if not rollback_statement:
                raise ParseError(self.get_rollback_fail)
            back_sqls += rollback_statement
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type_execute)
        execute_results = Inception(back_sqls, dbobj.name).inception_handle(db_addr).get('result')
        success_num = 0
        for result in execute_results:
            if result[4] == 'None':
                success_num += 1
        if success_num != len(execute_results):
            ret['status'] = -1
            status = -4
            roll_affected_rows = None
        else:
            status = -3
            roll_affected_rows = ret['data']['affected_rows'] = len(execute_results) - 1
        instance.status = status
        instance.handle_result_rollback = json.dumps(execute_results)
        instance.roll_affected_rows = roll_affected_rows
        self.replace_remark(instance)
        self.mail(instance, self.rollback.__name__)
        return Response(ret)