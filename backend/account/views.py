# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ParseError, AuthenticationFailed
from rest_framework.response import Response
from utils.permissions import IsSuperUser
from utils.basemixins import PromptMixins
from utils.baseviews import MaxSizePagination, BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.unitaryauth import UnitaryAuth
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

    def perform_update(self, serializer):
        serializer.update(self.get_object(), self.request.data)

    def perform_create(self, serializer):
        serializer.create(self.request.data)

class PersonalCenterViewSet(PromptMixins, BaseView):
    '''
        个人中心
    '''
    serializer_class = PersonalCenterSerializer

    def check_password(self, params):
        user = authenticate(username=self.request.user.username, password=params.get('old_pass'))
        if not user:
            raise ParseError(self.old_password_warning)
        new_pass = params.get('new_pass')
        rep_pass = params.get('rep_pass')
        if not (new_pass and rep_pass and new_pass == rep_pass):
            raise ParseError(self.new_rep_password_warning)
        return new_pass

    def list(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ret = res.get_ret()
        request_data = request.data
        new_pass = self.check_password(request_data)
        instance = request.user
        instance.set_password(new_pass)
        instance.save()
        return Response(ret)

class UnitaryAuthView(UnitaryAuth, APIView):
    '''
        接入统一登录
    '''
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        if not self.authenticate:
            raise AuthenticationFailed
        user_query = self.serializer_class.Meta.model.objects.filter(username=request.data.get('username'))
        if user_query:
            serializer = self.serializer_class(user_query[0], data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
