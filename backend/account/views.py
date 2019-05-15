# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError, AuthenticationFailed
from rest_framework.response import Response
from utils.permissions import IsSuperUser
from utils.basemixins import PromptMixin, AppellationMixin
from utils.baseviews import MaxSizePagination, BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.unitaryauth import UnitaryAuth
from utils.wrappers import permission_admin
from sqlmng.models import DbConf
from .serializers import *

class PermissionViewSet(AppellationMixin, BaseView):
    '''
        系统权限CURD
    '''
    pagination_class = MaxSizePagination
    queryset = DbConf.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        perms = user.userobjectpermission_set.all()
        db_id_list = [int(perm.object_pk) for perm in perms if perm]
        return self.queryset.filter(id__in=db_id_list)

class GroupViewSet(BaseView):
    '''
        系统组CURD
    '''
    queryset = Group.objects.order_by('-id')
    serializer_class = GroupSerializer
    permission_classes = [IsSuperUser]
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.create(self.request.data)

    def perform_update(self, serializer):
        serializer.update(self.get_object(), self.request.data)

class UserViewSet(BaseView):
    '''
        系统用户CURD
    '''
    queryset = User.objects.filter(is_staff=True).order_by('-id')
    serializer_class = UserSerializer
    search_fields = ['username']

    def perform_update(self, serializer):
        serializer.update(self.get_object(), self.request.data)

    @permission_admin
    def perform_create(self, serializer):
        serializer.create(self.request.data)

    @permission_admin
    def perform_destroy(self, instance):
        instance.delete()

class PersonalCenterViewSet(PromptMixin, BaseView):
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
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ret = res.get_ret()
        new_pass = self.check_password(request.data)
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
        request.data.update({'is_staff':True})
        serializer = self.serializer_class(data=request.data)
        user_query = self.serializer_class.Meta.model.objects.filter(username=request.data.get('username'))
        if user_query:
            serializer = self.serializer_class(user_query[0], data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
