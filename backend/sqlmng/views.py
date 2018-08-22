#coding=utf8
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from utils.baseviews import BaseView
from utils.basemixins import AppellationMixins
from utils.permissions import AuthOrReadOnly, IsSuperUser
from utils.inception import Inception
from account.serializers import UserSerializer
from .mixins import PromptMxins, ActionMxins
from .serializers import *
from .models import *
import re

class InceptionMainView(PromptMxins, ActionMxins, BaseView):
    '''
        查询：根据登录者身份返回相关的SQL，支持日期/模糊搜索。操作：执行（execute）, 回滚（rollback）,放弃（reject操作）
    '''
    serializer_class = InceptionSerializer
    permission_classes = [AuthOrReadOnly]
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

    @detail_route()
    def execute(self, request, *args, **kwargs):
        sqlobj = self.get_object()
        if sqlobj.status != -1:
            self.ret = {'status': -2, 'msg':self.executed}
            return Response(self.ret)
        affected_rows = 0
        execute_time = 0
        opids = []
        success_sqls, exception_sqls = self.check_execute_sql(sqlobj.db.id, sqlobj.sql_content)
        for success_sql in success_sqls:
            sqlobj.status = 0
            sqlobj.rollback_db = success_sql[8]
            affected_rows += success_sql[6]
            execute_time += float(success_sql[9])
            opids.append(success_sql[7].replace("'", ""))
        if exception_sqls:
            sqlobj.status = 2
            sqlobj.execute_errors = exception_sqls
            self.ret['status'] = -1
        sqlobj.rollback_opid = opids
        sqlobj.exe_affected_rows = affected_rows
        self.ret['data']['affected_rows'] = affected_rows
        self.ret['data']['execute_time'] = '%.3f' % execute_time
        self.ret['msg'] = exception_sqls
        self.mail(sqlobj, self.action_type)
        self.replace_remark(sqlobj)
        return Response(self.ret)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        sqlobj = self.get_object()
        sqlobj.status = 1
        self.replace_remark(sqlobj)
        return Response(self.ret)

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        sqlobj = self.get_object()
        dbobj = sqlobj.db
        rollback_opid_list = sqlobj.rollback_opid
        rollback_db = sqlobj.rollback_db
        back_sqls = ''
        for opid in eval(rollback_opid_list)[1:]:
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = Inception(back_source, rollback_db).get_back_table()
            back_content = 'select rollback_statement from {} where opid_time = "{}" '.format(back_table, opid)
            back_sqls += Inception(back_content, rollback_db).get_back_sql()
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)
        execute_results = Inception(back_sqls, dbobj.name).inception_handle(db_addr).get('result')
        sqlobj.status = -3
        sqlobj.roll_affected_rows = self.ret['data']['affected_rows'] = len(execute_results) - 1
        self.replace_remark(sqlobj)
        return Response(self.ret)

class InceptionCheckView(PromptMxins, ActionMxins, BaseView):
    '''
        审核 sql 的各类情形处理
    '''
    queryset = Inceptsql.objects.all()
    serializer_class = InceptionSerializer
    forbidden_word_list = ['use ', 'drop ']
    action_type = '--enable-check'

    def get_forbidden_words(self, sql_content):
        forbidden_words = [fword for fword in self.forbidden_word_list if re.search(re.compile(fword, re.I), sql_content)]
        if forbidden_words:
            raise ParseError({self.forbidden_words: forbidden_words})

    def check_user_group(self, request):
        if request.data.get('env') == self.env_prd and not request.user.is_superuser:
            if not request.user.groups.exists():
                raise ParseError(self.not_exists_group)
            return request.user.groups.first().id

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['group'] = self.check_user_group(request)
        request_data['treater'] = request_data.pop('treater_username')
        serializer = self.serializer_class(data = request_data)
        serializer.is_valid(raise_exception = True)
        sql_content = request_data.get('sql_content')
        self.get_forbidden_words(sql_content)
        self.check_execute_sql(request_data.get('db'), sql_content)
        sqlobj = serializer.save()
        self.mail(sqlobj, self.action_type)
        return Response(self.ret)

class SelectDataView(AppellationMixins, BaseView):
    '''
        根据前端的选择&用户身份返回check sql时需要的执行人，数据库数据
    '''
    queryset = Dbconf.objects.all()
    serializer_class = DbSerializer
    serializer_user = UserSerializer
    def create(self, request):
        env = request.data.get('env')
        qs = self.queryset.filter(env = env)
        self.ret['data']['dbs'] = self.serializer_class(qs, many = True).data
        userobj = request.user
        user_data = self.serializer_user(userobj).data
        self.ret['data']['commiter'] = user_data
        if userobj.is_superuser or env == self.env_test or userobj.role != self.dev:
            treaters = [user_data]
        else:
            group = userobj.groups.first()
            treaters = self.serializer_user(group.user_set.filter(role = self.dev_mng), many = True).data if group else []
        self.ret['data']['treaters'] = treaters
        return Response(self.ret)

class DbViewSet(BaseView):
    '''
        目标数据库的CURD
    '''
    queryset = Dbconf.objects.all()
    serializer_class = DbSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name','host','port','user','remark']
