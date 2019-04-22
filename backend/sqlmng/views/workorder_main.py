# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from utils.baseviews import BaseView
from workflow.serializers import StepSerializer
from sqlmng.mixins import CheckStatusMixin, ActionMixin, MailMixin
from sqlmng.permissions import IsHandleAble
from sqlmng.serializers import *
from sqlmng.models import *
from sqlmng.tasks import task_worker

class InceptionMainView(CheckStatusMixin, ActionMixin, MailMixin, BaseView):
    '''
        查询：根据登录者身份返回相关的工单，支持日期/模糊搜索。操作：执行（execute）, 回滚（rollback）,放弃（reject操作）
    '''
    serializer_class = ListInceptionSerializer
    serializer_step = StepSerializer
    permission_classes = [IsAuthenticated, IsHandleAble]
    search_fields = ['commiter', 'sql_content', 'env', 'treater', 'remark']

    def get_serializer_class(self):
        if self.kwargs.get('pk'):
            return DetailInceptionSerializer
        return ListInceptionSerializer

    def get_queryset(self):
        user_instance = self.request.user
        group_instance = user_instance.groups.first()
        if user_instance.is_superuser:
            return self.filter_date(InceptionWorkOrder.objects.all())
        instance = group_instance if user_instance.role == self.dev_spm else user_instance
        queryset = instance.inceptionworkorder_set.all() if instance else []
        return self.filter_date(queryset)

    @detail_route()
    def execute(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_status(instance)
        self.check_lock(instance)
        handle_type = instance.type or self.execute.__name__
        task_worker.delay(instance.id, 2, handle_type, request.user.id)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_status(instance)
        self.replace_remark(instance)
        role_step = self.get_reject_step(instance)
        self.handle_workflow(3,3,role_step)
        self.save_instance(instance, 1)
        self.mail(instance, self.reject.__name__, request.user, self.name_mail_inception)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_status(instance)
        self.handle_workflow(1,1,1)
        self.save_instance(instance, 3)
        self.mail(instance, self.approve.__name__, request.user, self.name_mail_inception)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def disapprove(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_status(instance)
        self.handle_workflow(1,2,1)
        self.save_instance(instance, 4)
        self.mail(instance, self.disapprove.__name__, request.user, self.name_mail_inception)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_status(instance)
        self.check_lock(instance)
        handle_type = self.rollback.__name__
        task_worker.delay(instance.id, 2, handle_type, request.user.id)
        return Response(self.serializer_class(instance).data)

    @detail_route(methods=['post'])
    def cron(self, request, *args, **kwargs):
        self.check_valid_date(request.data.get('cron_time'))
        instance = self.get_object()
        self.check_status(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        last_step = instance.work_order.step_set.first()
        username = settings.CELERY_BUSINESS_PARAMS.get('username')
        cron_user, _ = User.objects.get_or_create(username=username)
        if last_step and (not last_step.user == cron_user):
            last_step.user = request.user
            self.save_instance(last_step, 1)
            step_serializer = self.serializer_step(data={'work_order': instance.work_order.id, 'user': cron_user.id})
            step_serializer.is_valid(raise_exception=True)
            step_serializer.save()
        self.save_instance(instance, 5)
        return Response(self.serializer_class(instance).data)
