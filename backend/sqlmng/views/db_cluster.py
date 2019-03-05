# -*- coding: utf-8 -*-
from rest_framework.response import Response
from utils.baseviews import BaseView
from utils.permissions import IsSuperUser
from sqlmng.serializers import *
from sqlmng.models import *

class DbClusterViewSet(BaseView):
    '''
        数据库集群
    '''
    queryset = Cluster.objects.all()
    serializer_class = DbClusterSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name','remark']

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dbs = data.get('dbs')
        db_queryset = DbConf.objects.filter(id__in=dbs)
        instance.dbconf_set.set(db_queryset)
        return Response(self.serializer_class(instance).data)