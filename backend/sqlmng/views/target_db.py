#coding=utf8
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.sqltools import SqlQuery
from utils.permissions import IsSuperUser
from sqlmng.serializers import *
from sqlmng.models import *

class DbViewSet(BaseView):
    '''
        目标数据库的CURD
    '''
    serializer_class = DbSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name','host','port','user','remark']
    ret = res.get_ret()

    def get_queryset(self):
        env = self.request.GET.get('env')
        queryset = Dbconf.objects.all()
        if env:
            queryset = queryset.filter(env=env)
        return queryset

    @detail_route(methods=['post'])
    def sql_advisor(self, request, *args, **kwargs):
        instance = self.get_object()
        sql = request.data.get('sql')
        res = SqlQuery(instance).sql_advisor(sql)
        self.ret['results'] = res
        return Response(self.ret)

    @detail_route(methods=['post'])
    def sql_soar(self, request, *args, **kwargs):
        instance = self.get_object()
        sql = request.data.get('sql')
        soar_type = request.data.get('soar_type')
        res = SqlQuery(instance).sql_soar(sql, soar_type)
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