#coding=utf8
from rest_framework.response import Response
from utils.baseviews import BaseView
from account.serializers import UserSerializer
from sqlmng.serializers import *
from sqlmng.models import *

class SelectDataView(AppellationMixins, BaseView):
    '''
        根据前端的选择&用户身份返回check sql时需要的执行人，数据库数据
    '''
    queryset = Dbconf.objects.all()
    serializer_class = DbSerializer
    serializer_user = UserSerializer
    def create(self, request): 
        env = request.data.get('env')
        qs = self.queryset.filter(env = env)
        self.ret['data']['dbs'] = self.serializer_class(qs, many = True).data
        userobj = request.user
        user_data = self.serializer_user(userobj).data
        self.ret['data']['commiter'] = user_data
        if userobj.is_superuser or env == self.env_test or userobj.role != self.dev:
            treaters = [user_data]
        else:
            group = userobj.groups.first()
            treaters = self.serializer_user(group.user_set.filter(role = self.dev_mng), many = True).data if group else []
        self.ret['data']['treaters'] = treaters
        return Response(self.ret)
