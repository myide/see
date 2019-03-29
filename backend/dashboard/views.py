# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.response import Response
from utils.baseviews import ReturnFormatMixin as res
from utils.baseviews import MaxSizePagination, BaseView
from sqlmng.models import InceptionWorkOrder
from sqlmng.serializers import *
from account.serializers import *
from .mixins import HandleData

class ChartViewSet(HandleData, BaseView):
    '''
        Dashboard 查询
    '''
    pagination_class = MaxSizePagination
    queryset = InceptionWorkOrder.objects.all()
    serializer_user = UserSerializer
    serializer_group = GroupSerializer
    serializer_class = ListInceptionSerializer

    def list(self, request, *args, **kwargs):
        ret = res.get_ret()
        ret['data']['user_info'] = self.get_user_info
        ret['data']['count_data'] = self.get_count_data
        ret['data']['sql_status_data'] = self.get_status_data
        ret['data']['sql_trend_data'] = self.get_trend_data
        ret['data']['sql_today_data'] = self.get_today_data
        ret['data']['sql_type_data'] = self.get_type_data
        return Response(ret)
