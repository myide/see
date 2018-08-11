#coding=utf8
from rest_framework import permissions
from sqlmng.models import Inceptsql
from utils.basemixins import AppellationMixins

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class AuthOrReadOnly(AppellationMixins, permissions.BasePermission):

    def __init__(self):
        # 权限名
        self.allperms = ['execute', 'rollback', 'reject']
        # 权限规则
        self.auths = {
            self.dev: ['reject'],
            self.dev_mng: self.allperms,
            self.dev_spm: self.allperms,
        }

    def has_permission(self, request, view):
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if uri not in self.allperms:
            return True
        pk = uri_list[-3]
        sqlobj = Inceptsql.objects.get(pk = pk)
        if sqlobj.env == self.env_test:
            return True
        return uri in self.auths[request.user.role] or request.user.is_superuser

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
