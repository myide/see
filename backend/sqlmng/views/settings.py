# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from guardian.models import UserObjectPermission
from utils.baseviews import BaseView
from utils.basemixins import PromptMixin
from utils.baseviews import ReturnFormatMixin as res
from utils.permissions import IsSuperUser
from sqlmng.mixins import FixedDataMixin, CheckConn, HandleInceptionSettingsMixin, PermissionDatabases
from sqlmng.data import *
from sqlmng.serializers import *
from sqlmng.models import *

class SqlSettingsViewSet(FixedDataMixin, BaseView):
    '''
        设置SQL语句的属性（数量，拦截的字段）
    '''
    serializer_class = SqlSettingsSerializer
    permission_classes = [IsSuperUser]
    source_data = sql_settings

class StrategyViewSet(BaseView):
    '''
        设置审批策略
    '''
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsSuperUser]

class PersonalSettingsViewSet(PromptMixin, BaseView):
    '''
        审核工单的用户个性化设置
    '''
    serializer_class = PersonalSerializer

    def get_queryset(self):
        return [self.request.user]

    def check_data(self, request_data):
        cluster = request_data.get('cluster')
        dbs = request_data.get('dbs')
        env = request_data.get('env')
        return cluster, dbs, env

    def create(self, request, *args, **kwargs):
        user = request.user
        user_serializer = self.serializer_class(user, data=request.data)
        user_serializer.is_valid()
        user_serializer.save()
        cluster, dbs, env = self.check_data(request.data)
        if cluster:
            alter_qs = user.dbconf_set.filter(cluster=cluster, env=env)
            for obj in alter_qs:
                user.dbconf_set.remove(obj)
            for db_id in dbs:
                user.dbconf_set.add(db_id)
        return Response(res.get_ret())

class InceptionVariablesViewSet(FixedDataMixin, HandleInceptionSettingsMixin, BaseView):
    '''
        Inception 变量
    '''
    serializer_class = InceptionVariablesSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name']
    source_data = variables

    def create(self, request, *args, **kwargs):
        self.set_variable(request)
        return Response(res.get_ret())

class MailActionsSettingsViewSet(FixedDataMixin, BaseView):
    '''
        发邮件对应的动作
    '''
    serializer_class = MailActionsSettingsSerializer
    permission_classes = [IsSuperUser]
    source_data = mail_actions

    def create(self, request, *args, **kwargs):
        model = self.serializer_class.Meta.model
        model.objects.all().update(value=False)
        model.objects.filter(name__in=request.data).update(value=True)
        return Response(res.get_ret())

class InceptionConnectionViewSet(BaseView):
    '''
        Inception连接信息
    '''
    queryset = InceptionConnection.objects.all()
    serializer_class = InceptionConnectionSerializer
    permission_classes = [IsSuperUser]

class InceptionBackupView(HandleInceptionSettingsMixin, APIView):
    '''
        Inception备份信息
    '''
    def get(self, request, *args, **kwargs):
        ret = res.get_ret()
        ret['data'] = self.get_inception_backup()
        return Response(ret)

class ConnectionCheckView(CheckConn, APIView):
    '''
        检查连接(Inception连接/Inception备份库/目标库)
    '''
    def post(self, request, *args, **kwargs):
        check_type = request.data.pop('check_type')
        func = getattr(CheckConn, check_type)
        ret = func(self, request)
        return Response(ret)

class ShowDatabasesView(CheckConn, APIView):
    '''
        获取host地址的所有数据库
    '''
    def post(self, request, *args, **kwargs):
        ret = self.get_db_list(request)
        return Response(ret)
