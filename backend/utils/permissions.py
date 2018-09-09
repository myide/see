#coding=utf8
from rest_framework import permissions
from sqlmng.models import *
from utils.basemixins import AppellationMixins

reject_perms = ['reject']
approve_perms = ['approve', 'disapprove']
handle_perms = ['execute', 'rollback']
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class AuthOrReadOnly(AppellationMixins, permissions.BasePermission):
    pass

class IsHandleAble(AppellationMixins, permissions.BasePermission):

    def __init__(self):
        pass

    def has_object_permission(self, request, view, obj):
        """
            在调get_object()时检查该权限（get_object -- check_object_permissions -- has_object_permission）
        """
        env = obj.env
        is_manual_review = obj.is_manual_review
        role = self.admin if request.user.is_superuser else request.user.role
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if obj.is_manual_review == True:
            approve_step_instance = obj.step_set.all()[1]
            approve_user = approve_step_instance.user 
            if uri in handle_perms: 
                if not obj.handleable:
                    return False
                if approve_user == request.user: 
                    return False
            elif uri in approve_perms: 
                if approve_user != request.user:
                    return False
        return request.method in SAFE_METHODS or self.check_perm(env, is_manual_review, role, uri)

    def check_perm(self, env, is_manual_review, role, uri):
        try:
            perm_obj = AuthRules.objects.get(env=env, is_manual_review=is_manual_review, role=role)
            perm_serializer = AuthRulesSerializer(perm_obj)
            return perm_serializer.data.get(uri)
        except Exception as e:
            return False

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
