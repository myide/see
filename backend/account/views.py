# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils.permissions import IsSuperUser
from utils.baseviews import MaxSizePagination, BaseView
from .serializers import *

# Create your views here.

class PermissionViewSet(BaseView):
    '''
        系统权限CURD
    '''
    pagination_class = MaxSizePagination
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperUser]

class GroupViewSet(BaseView):
    '''
        系统组CURD
    '''
    queryset = Group.objects.all().order_by('-id')
    serializer_class = GroupSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name']

class UserViewSet(BaseView):
    '''
        系统用户CURD
    '''
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['username']
