#coding=utf8
from rest_framework.response import Response
from utils.baseviews import BaseView
from utils.permissions import IsSuperUser
from sqlmng.serializers import *
from sqlmng.models import *

class ForbiddenWordsViewSet(BaseView):
    '''
        设置SQL语句中需拦截的字段
    '''
    queryset = ForbiddenWords.objects.all()
    serializer_class = ForbiddenWordsSerializer
    permission_classes = [IsSuperUser]

class StrategyViewSet(BaseView):
    '''
        设置审批策略
    '''
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsSuperUser]

class PersonalSettingsViewSet(BaseView):
    '''
        审核工单的用户个性化设置
    '''
    serializer_class = PersonalSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request_data = request.data
        instance = request.user
        user_serializer = self.serializer_class(instance, data={'leader':request_data.get('leader')})
        user_serializer.is_valid()
        user_serializer.save()
        instance.dbconf_set.set(request_data.get('dbs'))
        instance.save()
        return Response(self.ret)
