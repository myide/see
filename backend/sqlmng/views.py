#coding=utf8
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from utils.baseviews import BaseView
from utils.basemixins import AppellationMixins
from utils.permissions import AuthOrReadOnly, IsSuperUser, IsHandleAble
from utils.sqltools import Inception, SqlQuery
from account.serializers import UserSerializer
from .mixins import PromptMxins, ActionMxins
from .serializers import *
from .models import *
import re

class InceptionMainView(PromptMxins, ActionMxins, BaseView):
    serializer_class = InceptionSerializer
    permission_classes = [IsHandleAble, AuthOrReadOnly]
    search_fields = ['commiter', 'sql_content', 'env', 'treater', 'remark']
    action_type = '--enable-execute'

    def filter_date(self, queryset):
        date_range = self.request.GET.get('daterange')
        if date_range:
            return queryset.filter(createtime__range = date_range.split(','))
        return queryset

    def get_queryset(self):
        userobj = self.request.user
        if userobj.is_superuser:  # 管理员
            return self.filter_date(Inceptsql.objects.all())
        query_set = userobj.groups.first().inceptsql_set.all() if userobj.role == self.dev_spm else userobj.inceptsql_set.all()
        return self.filter_date(query_set)

    def check_approve_status(self, instance):
        step_instance = instance.step_set.all()[1]
        if step_instance.status != 0:
            raise ParseError(self.approve_warning)

    def handle_approve(self, call_type, status, step_number):
        instance = self.get_object()
        if call_type == 1:  # 审批的
            self.check_approve_status(instance)
            if status == 1:
                instance.handleable = True
                instance.save()
        if instance.env == self.env_prd:
            step_instance = instance.step_set.order_by('id')[step_number]
            step_instance.status = status
            step_instance.save()

    @detail_route()
    def execute(self, request, *args, **kwargs):
        instance = self.get_object()
        # 执行SQL（防止同一个SQL被人已执行了，这边还没刷新 但点了执行，产生bug。执行前先检查status）
        if instance.status != -1:
            self.ret = {'status': -2, 'msg':self.executed}
            return Response(self.ret)
        affected_rows = 0
        execute_time = 0
        opids = []
        success_sqls, exception_sqls = self.check_execute_sql(instance.db.id, instance.sql_content)
        for success_sql in success_sqls:
            instance.status = 0
            # 执行结果，受影响的条数，执行所耗时间，回滚语句
            instance.rollback_db = success_sql[8]
            affected_rows += success_sql[6]
            execute_time += float(success_sql[9])
            opids.append(success_sql[7].replace("'", ""))  # execute_sql[7].replace("'","")  : 每条sql执行后的回滚opid
        if exception_sqls:
            instance.status = 2
            instance.execute_errors = exception_sqls
            self.ret['status'] = -1
        instance.rollback_opid = opids
        instance.exe_affected_rows = affected_rows
        self.ret['data']['affected_rows'] = affected_rows
        self.ret['data']['execute_time'] = '%.3f' % execute_time # 保留3位小数
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
        rollback_db = instance.rollback_db  # 回滚库
        # 拼接回滚语句
        back_sqls = ''  # 回滚语句
        for opid in eval(rollback_opid_list)[1:]:
            # 1 从回滚总表中获取表名
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = Inception(back_source, rollback_db).get_back_table()
            # 2 从回滚子表中获取回滚语句
            back_content = 'select rollback_statement from {} where opid_time = "{}" '.format(back_table, opid)
            back_sqls += Inception(back_content, rollback_db).get_back_sql()
        # 拼接回滚语句 执行回滚操作，修改sql状态
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)
        execute_results = Inception(back_sqls, dbobj.name).inception_handle(db_addr).get('result')
        instance.status = -3
        instance.roll_affected_rows = self.ret['data']['affected_rows'] = len(execute_results) - 1  # 执行回滚语句的结果，除去第一个use 数据库的
        self.replace_remark(instance)
        return Response(self.ret)

class InceptionCheckView(PromptMxins, ActionMxins, BaseView):
    queryset = Inceptsql.objects.all()
    serializer_class = InceptionSerializer
    serializer_step = StepSerializer
    action_type = '--enable-check'

    def check_forbidden_words(self, sql_content):
        forbidden_word_list = [fword for fword in ForbiddenWords.objects.first().forbidden_words.split(' ') if fword]
        forbidden_words = [fword for fword in forbidden_word_list if re.search(re.compile(fword, re.I), sql_content)]
        if forbidden_words:
            raise ParseError({self.forbidden_words: forbidden_words})

    def check_user_group(self, request):
        if request.data.get('env') == self.env_prd and not request.user.is_superuser:
            if not request.user.groups.exists():
                raise ParseError(self.not_exists_group)
            return request.user.groups.first().id

    def create_step(self, instance, users_id):
        if self.is_manual_review and instance.env == self.env_prd:  # 有审批流程且是生产环境
            instance_id = instance.id
            users_id.append(None)
            for index, uid in enumerate(users_id):
                status = 1 if index == 0 else 0  # 第一个step的状态是1
                step_serializer = self.serializer_step(data={'work_order':instance_id, 'user':uid, 'status':status})
                step_serializer.is_valid(raise_exception=True)
                step_serializer.save()

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['group'] = self.check_user_group(request)
        request_data['treater'] = request_data.pop('treater_username')
        serializer = self.serializer_class(data = request_data)
        serializer.is_valid(raise_exception = True)
        sql_content = request_data.get('sql_content')
        # 禁止词过滤
        self.check_forbidden_words(sql_content)
        # inception检查
        self.check_execute_sql(request_data.get('db'), sql_content)
        # 审核通过，写入数据库
        instance = serializer.save()
        # 创建step
        self.create_step(instance, request_data['users'])
        self.mail(instance, self.action_type)
        return Response(self.ret)

class SelectDataView(AppellationMixins, BaseView):
    queryset = Dbconf.objects.all()
    serializer_class = DbSerializer
    serializer_user = UserSerializer
    def create(self, request):  # 前端切换环境时，返回相应的数据（执行人，数据库名）
        env = request.data.get('env')
        qs = self.queryset.filter(env = env)
        self.ret['data']['dbs'] = self.serializer_class(qs, many = True).data
        userobj = request.user
        user_data = self.serializer_user(userobj).data
        self.ret['data']['commiter'] = user_data
        if userobj.is_superuser or env == self.env_test or userobj.role != self.dev:  # 超级用户 or 测试环境 or 除开发外，执行人是自己
            treaters = [user_data]
        else:
            group = userobj.groups.first()
            treaters = self.serializer_user(group.user_set.filter(role = self.dev_mng), many = True).data if group else []
        self.ret['data']['treaters'] = treaters
        return Response(self.ret)

class DbViewSet(BaseView):
    serializer_class = DbSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name','host','port','user','remark']
    def get_queryset(self):
        env = self.request.GET.get('env')
        queryset = Dbconf.objects.all()
        if env:
            queryset = queryset.filter(env=env)
        return queryset

    @detail_route()
    def sql_advisor(self, request, *args, **kwargs):
        instance = self.get_object()
        sql = request.GET.get('sql')
        res = SqlQuery(instance).sql_advisor(sql)
        self.ret['results'] = res
        return Response(self.ret)

    @detail_route()
    def tables(self, request, *args, **kwargs ):
        instance = self.get_object()
        tables = SqlQuery(instance).get_tables()
        self.ret['results'] = tables
        return Response(self.ret)

    @detail_route()
    def table_info(self, request, *args, **kwargs ):
        instance = self.get_object()
        table_name = request.GET.get('table_name')
        table_info = SqlQuery(instance).get_table_info(table_name)
        self.ret['results'] = table_info
        return Response(self.ret)

class ForbiddenWordsViewSet(BaseView):
    queryset = ForbiddenWords.objects.all()
    serializer_class = ForbiddenWordsSerializer
    permission_classes = [IsSuperUser]

class StrategyViewSet(BaseView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsSuperUser]

class StepViewSet(BaseView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer

class PersonalSettingsViewSet(BaseView):
    serializer_class = PersonalSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        # save user
        request_data = request.data
        instance = request.user
        user_serializer = self.serializer_class(instance, data={'leader':request_data.get('leader')})
        user_serializer.is_valid()
        user_serializer.save()
        # save dbconf
        instance.dbconf_set.set(request_data.get('dbs'))
        instance.save()
        return Response(self.ret)
