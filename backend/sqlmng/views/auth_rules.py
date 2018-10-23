#coding=utf8
from utils.baseviews import BaseView
from sqlmng.serializers import *
from sqlmng.data import auth_rules

class AuthRulesViewSet(BaseView):
    '''
        平台权限
    '''
    serializer_class = AuthRulesSerializer
    search_fields = ['env']

    def get_queryset(self):
        model = self.serializer_class.Meta.model
        objects = model.objects
        queryset = objects.all()
        if queryset.count() != 16:
            queryset.delete()
            auths = [model(**auth) for auth in auth_rules]
            objects.bulk_create(auths)
            queryset = objects.all()
        return queryset