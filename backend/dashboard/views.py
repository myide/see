# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Count, Q
from rest_framework.response import Response
from utils.baseviews import ReturnFormatMixin as res
from utils.baseviews import MaxSizePagination, BaseView
from sqlmng.models import Inceptsql
from sqlmng.serializers import *
from account.serializers import *
from utils.sqltools import Inception
import datetime
# Create your views here.

class ChartViewSet(BaseView):
    '''
        Dashboard 查询
    '''
    pagination_class = MaxSizePagination
    queryset = Inceptsql.objects.all()
    serializer_user = UserSerializer
    serializer_group = GroupSerializer
    serializer_class = InceptionSerializer

    def get_user_info(self):
        user_obj = self.request.user
        user_info = {}
        user_info['username'] = user_obj.username
        user_info['date_joined'] = user_obj.date_joined
        user_info['group'] = user_obj.groups.first().name if user_obj.groups.first() else None
        user_info['identity'] = 'superuser' if user_obj.is_superuser else user_obj.role
        return user_info

    def get_count_data(self):
        count_data = {}
        count_data['sql_total'] = self.queryset.count()
        count_data['sql_handled'] = self.queryset.filter(~Q(status = -1) & ~Q(status = -2)).count()
        count_data['user_total'] = self.serializer_user.Meta.model.objects.all().count()
        count_data['group_total'] = self.serializer_group.Meta.model.objects.all().count()
        return count_data

    def get_status_data(self):
        return self.queryset.values('status').annotate(num = Count('status')).order_by()

    def get_trend_data(self):
        date_range = range(14)
        date_list = []
        times_list = []
        for day in reversed(date_range):
            date_time = datetime.datetime.now() - datetime.timedelta(days = day)
            date = date_time.strftime("%Y-%m-%d")
            times = self.queryset.filter(createtime__startswith = date).count()
            date_list.append(date)
            times_list.append(times)
        return {'date_list':date_list, 'times_list':times_list}

    def get_today_data(self):
        date_time = datetime.datetime.now() - datetime.timedelta(days = 0)
        date = date_time.strftime("%Y-%m-%d")
        qs_today = self.queryset.filter(createtime__startswith = date)
        return self.serializer_class(qs_today, many = True).data

    def get_type_data(self):
        index_list = Inception('desc inception.statistic').get_index_list()
        index_data = []
        for index in index_list:
            sql = 'SELECT `statistic`.`{}`, COUNT(`statistic`.`{}`) ' \
                  'AS `num` FROM `statistic` WHERE {} > 0 ' \
                  'GROUP BY `statistic`.`{}` ORDER BY NULL;'\
                .format(index, index, index, index)
            records = Inception(sql, 'inception').manual()
            total_execute_counts = 0
            total_execute_times = 0
            if records:
                for record in records:
                    total_execute_counts += record[0] * record[1]
                    total_execute_times += record[1]
            index_data.append(
                {
                    'index':index,
                    'total_execute_counts':total_execute_counts,
                    'total_execute_times':total_execute_times
                })
        return index_data

    def list(self, request, *args, **kwargs):
        ret = res.get_ret()
        ret['data']['user_info'] = self.get_user_info()
        ret['data']['count_data'] = self.get_count_data()
        ret['data']['sql_status_data'] = self.get_status_data()
        ret['data']['sql_trend_data'] = self.get_trend_data()
        ret['data']['sql_today_data'] = self.get_today_data()
        ret['data']['sql_type_data'] = self.get_type_data()
        return Response(ret)
