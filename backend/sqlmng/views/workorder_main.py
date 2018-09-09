#coding=utf8
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from utils.baseviews import BaseView
from utils.permissions import AuthOrReadOnly, IsHandleAble
from utils.sqltools import Inception
from sqlmng.mixins import PromptMxins, ActionMxins
from sqlmng.serializers import *
from sqlmng.models import *

class InceptionMainView(PromptMxins, ActionMxins, BaseView):
    '''
        查询：根据登录者身份返回相关的SQL，支持日期/模糊搜索。操作：执行（execute）, 回滚（rollback）,放弃（reject操作）
    '''
    serializer_class = InceptionSerializer
    permission_classes = [IsHandleAble] 
    search_fields = ['commiter', 'sql_content', 'env', 'treater', 'remark']
    action_type = '--enable-execute'

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
        step_instance = instance.step_set.all()[1]
        if step_instance.status != 0:
            raise ParseError(self.approve_warning)

    def handle_approve(self, call_type, status, step_number):
        instance = self.get_object()
        if instance.is_manual_review == True and instance.env == self.env_prd:
            if call_type == 1:
                self.check_approve_status(instance)
                if status == 1:
                    instance.handleable = True
                    instance.save()
            if instance.env == self.env_prd and instance.is_manual_review == True:
                step_instance = instance.step_set.order_by('id')[step_number]
                step_instance.status = status
                step_instance.save()

    @detail_route()
    def execute(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != -1:
            self.ret = {'status': -2, 'msg':self.executed}
            return Response(self.ret)
        affected_rows = 0
        execute_time = 0
        opids = []
        success_sqls, exception_sqls = self.check_execute_sql(instance.db.id, instance.sql_content)
        for success_sql in success_sqls:
            instance.status = 0
            instance.rollback_db = success_sql[8]
            affected_rows += success_sql[6]
            execute_time += float(success_sql[9])
            opids.append(success_sql[7].replace("'", "")) 
        if exception_sqls:
            instance.status = 2
            instance.execute_errors = exception_sqls
            self.ret['status'] = -1
        instance.rollback_opid = opids
        instance.exe_affected_rows = affected_rows
        self.ret['data']['affected_rows'] = affected_rows
        self.ret['data']['execute_time'] = '%.3f' % execute_time 
        self.ret['msg'] = exception_sqls
        self.mail(instance, self.action_type)
        self.replace_remark(instance)
        self.handle_approve(2,1,2)
        return Response(self.ret)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 1
        self.replace_remark(instance)
        return Response(self.ret)

    @detail_route()
    def approve(self, request, *args, **kwargs):
        self.handle_approve(1,1,1)
        return Response(self.ret)

    @detail_route()
    def disapprove(self, request, *args, **kwargs):
        self.handle_approve(1,2,1)
        return Response(self.ret)

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        instance = self.get_object()
        dbobj = instance.db
        rollback_opid_list = instance.rollback_opid
        rollback_db = instance.rollback_db 
        back_sqls = '' 
        for opid in eval(rollback_opid_list)[1:]:
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = Inception(back_source, rollback_db).get_back_table()
            back_content = 'select rollback_statement from {} where opid_time = "{}" '.format(back_table, opid)
            back_sqls += Inception(back_content, rollback_db).get_back_sql()
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)
        execute_results = Inception(back_sqls, dbobj.name).inception_handle(db_addr).get('result')
        instance.status = -3
        instance.roll_affected_rows = self.ret['data']['affected_rows'] = len(execute_results) - 1 
        self.replace_remark(instance)
        return Response(self.ret)
