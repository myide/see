# -*- coding: utf-8 -*-
from rest_framework.response import Response
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.basemixins import AppellationMixin
from account.serializers import UserSerializer
from sqlmng.serializers import DbSerializer
from sqlmng.mixins import PermissionDatabases
from sqlmng.models import *

class SelectDataView(AppellationMixin, PermissionDatabases, BaseView):
    '''
        根据用户身份返回check sql时需要的执行人，数据库数据
    '''
    queryset = DbConf.objects.all()
    serializer_class = DbSerializer
    serializer_user = UserSerializer

    def create(self, request, *args, **kwargs):
        ret = res.get_ret()
        env = request.data.get('env')
        cluster = request.data.get('cluster') or None
        qs_db = self.queryset.filter(env=env, cluster_id=cluster)
        qs_db = self.filter_databases(qs_db)
        qs_admin = self.serializer_user.Meta.model.objects.filter(is_superuser=True)
        ret['data']['dbs'] = self.serializer_class(qs_db, many=True).data
        ret['data']['admins'] = self.serializer_user(qs_admin, many=True).data
        user_instance = request.user
        user_data = self.serializer_user(user_instance).data
        ret['data']['commiter'] = user_data
        if user_instance.is_superuser or env == self.env_test or user_instance.role != self.dev:
            treaters = [user_data]
        else:
            group = user_instance.groups.first()
            treaters = self.serializer_user(group.user_set.filter(role=self.dev_mng), many=True).data if group else []
        ret['data']['treaters'] = treaters
        return Response(ret)
