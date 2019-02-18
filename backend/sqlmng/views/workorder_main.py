#coding=utf8
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from utils.baseviews import BaseView
from workflow.serializers import StepSerializer
from sqlmng.mixins import ActionMixins
from sqlmng.permissions import IsHandleAble
from sqlmng.serializers import *
from sqlmng.models import *
from sqlmng.tasks import task_worker

class InceptionMainView(ActionMixins, BaseView):
    '''
        查询：根据登录者身份返回相关的SQL，支持日期/模糊搜索。操作：执行（execute）, 回滚（rollback）,放弃（reject操作）
    '''
    serializer_class = InceptionSerializer
    serializer_step = StepSerializer
    permission_classes = [IsAuthenticated, IsHandleAble]
    search_fields = ['commiter', 'sql_content', 'env', 'treater', 'remark']

    def get_queryset(self):
        userobj = self.request.user
        if userobj.is_superuser:
            return self.filter_date(Inceptsql.objects.all())
        query_set = userobj.groups.first().inceptsql_set.all() if userobj.role == self.dev_spm else userobj.inceptsql_set.all()
        return self.filter_date(query_set)

    @detail_route()
    def execute(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_lock(instance)
        self.check_status(instance)
        handle_type = instance.type or self.execute.__name__
        task_worker.delay(instance.id, 2, handle_type, request.user.id)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        self.replace_remark(instance)
        role_step = self.get_reject_step(instance)
        self.handle_workflow(3,3,role_step)
        self.save_instance(instance, 1)
        self.mail(instance, self.reject.__name__, request.user)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.handle_workflow(1,1,1)
        self.save_instance(instance, 3)
        self.mail(instance, self.approve.__name__, request.user)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def disapprove(self, request, *args, **kwargs):
        instance = self.get_object()
        self.handle_workflow(1,2,1)
        self.save_instance(instance, 4)
        self.mail(instance, self.disapprove.__name__, request.user)
        return Response(self.serializer_class(instance).data)

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        instance = self.get_object()
        handle_type = self.rollback.__name__
        task_worker.delay(instance.id, 2, handle_type, request.user.id)
        return Response(self.serializer_class(instance).data)

    @detail_route(methods=['post'])
    def cron(self, request, *args, **kwargs):
        self.check_valid_date(request.data.get('cron_time'))
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        last_step = instance.workorder.step_set.all()[0]
        username = settings.CELERY_BUSINESS_PARAMS.get('username')
        cron_user, _ = User.objects.get_or_create(username=username)
        if not last_step.user == cron_user:
            last_step.user = request.user
            self.save_instance(instance, 5)
            self.save_instance(last_step, 1)
            step_serializer = self.serializer_step(data={'work_order': instance.workorder.id, 'user': cron_user.id})
            step_serializer.is_valid(raise_exception=True)
            step_serializer.save()
        return Response(self.serializer_class(instance).data)
