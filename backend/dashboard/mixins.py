# -*- coding: utf-8 -*-
import datetime
from django.db.models import Count, Q
from utils.sqltools import Inception

class HandleData(object):

    @property
    def get_user_info(self):
        user_instance = self.request.user
        user_info = dict()
        user_group = user_instance.groups.first()
        user_info['username'] = user_instance.username
        user_info['date_joined'] = user_instance.date_joined
        user_info['group'] = user_group.name if user_group else None
        user_info['identity'] = 'superuser' if user_instance.is_superuser else user_instance.role
        return user_info

    @property
    def get_count_data(self):
        count_data = dict()
        count_data['sql_total'] = self.queryset.count()
        count_data['sql_handled'] = self.queryset.filter(~Q(status=-1) & ~Q(status=-2)).count()
        count_data['user_total'] = self.serializer_user.Meta.model.objects.all().count()
        count_data['group_total'] = self.serializer_group.Meta.model.objects.all().count()
        return count_data

    @property
    def get_status_data(self):
        return self.queryset.values('status').annotate(num=Count('status')).order_by()

    @property
    def get_trend_data(self):
        date_range = range(14)
        date_list = []
        times_list = []
        for day in reversed(date_range):
            date_time = datetime.datetime.now() - datetime.timedelta(days=day)
            date = date_time.strftime("%Y-%m-%d")
            times = self.queryset.filter(createtime__startswith=date).count()
            date_list.append(date)
            times_list.append(times)
        return {'date_list':date_list, 'times_list':times_list}

    @property
    def get_today_data(self):
        date_time = datetime.datetime.now() - datetime.timedelta(days=0)
        date = date_time.strftime("%Y-%m-%d")
        qs_today = self.queryset.filter(createtime__startswith=date)
        return self.serializer_class(qs_today, many=True).data

    @property
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