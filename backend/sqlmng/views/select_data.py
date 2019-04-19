# -*- coding: utf-8 -*-
from rest_framework.response import Response
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.basemixins import AppellationMixin
from account.serializers import UserSerializer
from sqlmng.serializers import DbSerializer
from sqlmng.models import *

class SelectDataView(AppellationMixin, BaseView):
    '''
        根据用户身份返回check sql时需要的执行人，数据库数据
    '''
    queryset = DbConf.objects.all()
    serializer_class = DbSerializer
    serializer_user = UserSerializer

    def get_permission_databases(self):
        user = self.request.user
        group = user.groups.first()
        user_perms = user.userobjectpermission_set.all()
        group_perms = group.groupobjectpermission_set.all() if group else []
        user_perms_set = set([perm.object_pk for perm in user_perms])
        group_perms_set = set([perm.object_pk for perm in group_perms])
        return user_perms_set | group_perms_set

    def create(self, request, *args, **kwargs):
        ret = res.get_ret()
        env = request.data.get('env')
        cluster = request.data.get('cluster') or None
        qs_db = self.queryset.filter(env=env, cluster_id=cluster)
        perm_dbs = self.get_permission_databases()
        qs_db = [db for db in qs_db if str(db.id) in perm_dbs]
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
