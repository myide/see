# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework_bulk.drf3.mixins import BulkCreateModelMixin
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.sqltools import SqlQuery
from utils.permissions import IsSuperUser
from sqlmng.mixins import GuardianPermission, CheckStatusMixin, MailMixin, PermissionDatabases
from sqlmng.serializers import *
from sqlmng.models import *

class DbViewSet(PermissionDatabases, GuardianPermission, BulkCreateModelMixin, BaseView):
    '''
        目标数据库CURD
    '''
    serializer_class = DbSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name','host','port','user','remark']
    ret = res.get_ret()

    def perform_destroy(self, instance):
        self.delete_relation(instance)
        instance.delete()

    def get_queryset(self):
        user = self.request.user
        queryset = DbConf.objects.all()
        env = self.request.GET.get('env')
        if env:
            queryset = queryset.filter(env=env)
        if user.is_superuser:
            return queryset
        return self.filter_databases(queryset)

    @detail_route(methods=['post'], permission_classes=[])
    def sql_advisor(self, request, *args, **kwargs):
        instance = self.get_object()
        sql = request.data.get('sql')
        res = SqlQuery(instance).sql_advisor(sql)
        self.ret['results'] = res
        return Response(self.ret)

    @detail_route(methods=['post'], permission_classes=[])
    def sql_soar(self, request, *args, **kwargs):
        instance = self.get_object()
        sql = request.data.get('sql')
        soar_type = request.data.get('soar_type')
        res = SqlQuery(instance).sql_soar(sql, soar_type)
        self.ret['results'] = res
        return Response(self.ret)

    @detail_route()
    def tables(self, request, *args, **kwargs):
        instance = self.get_object()
        tables = SqlQuery(instance).get_tables()
        self.ret['results'] = tables
        return Response(self.ret)

    @detail_route()
    def table_info(self, request, *args, **kwargs):
        instance = self.get_object()
        table_name = request.GET.get('table_name')
        table_info = SqlQuery(instance).get_table_info(table_name)
        self.ret['results'] = table_info
        return Response(self.ret)

    @detail_route()
    def relate_permission(self, request, *args, **kwargs):
        instance = self.get_object()
        self.ret['results'] = self.get_related_status(instance)
        return Response(self.ret)

class DbWorkOrderViewSet(CheckStatusMixin, MailMixin, BaseView):
    '''
        数据库工单CURD
    '''
    serializer_class = DbWorkOrderSerializer
    permission_classes = []
    search_fields = ['name','remark']

    def get_queryset(self):
        queryset = DatabaseWorkOrder.objects.all()
        user = self.request.user
        if not user.is_superuser:
            queryset = queryset.filter(commiter=user)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        self.handle_mail(self.db_order_apply, instance)

    def perform_update(self, serializer):
        if self.get_object().status:
            raise ParseError(self.not_edit_status)
        serializer.save()

    def handle_mail(self, db_order_type, instance=None):
        instance = instance or self.get_object()
        self.mail(instance, db_order_type, self.request.user, self.name_mail_db_order)

    def handle_order(self):
        instance = self.get_object()
        self.check_status(instance)
        serializer = self.get_serializer(instance, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @detail_route(methods=['post'], permission_classes=[IsSuperUser])
    def database_order_approve(self, request, *args, **kwargs):
        serializer = self.handle_order()
        self.handle_mail(self.db_order_approve)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsSuperUser])
    def database_order_disapprove(self, request, *args, **kwargs):
        serializer = self.handle_order()
        self.handle_mail(self.db_order_disapprove)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[])
    def database_order_reject(self, request, *args, **kwargs):
        serializer = self.handle_order()
        self.handle_mail(self.db_order_reject)
        return Response(serializer.data)
