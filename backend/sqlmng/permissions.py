#coding=utf8
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from utils.permissions import SAFE_METHODS
from utils.basemixins import AppellationMixins, PromptMxins
from sqlmng.serializers import AuthRulesSerializer
from sqlmng.mixins import ActionMxins
from sqlmng.data import step_rules
from sqlmng.models import *

reject_perms = ['reject']
approve_perms = ['approve', 'disapprove']
handle_perms = ['execute', 'rollback']

class IsHandleAble(AppellationMixins, permissions.BasePermission):

    def __init__(self):
        pass

    def parse_result(self, has_auth, desc):
        if not has_auth:
            raise PermissionDenied(desc)
        else:
            return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        env = obj.env
        is_manual_review = obj.is_manual_review
        role = self.admin if user.is_superuser else user.role
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if (request.method in SAFE_METHODS and uri not in reject_perms + approve_perms + handle_perms) or env == self.env_test:
            return True
        if obj.is_manual_review == True:
            approve_step_instance = obj.workorder.step_set.all()[1]
            approve_user = approve_step_instance.user
            if uri in handle_perms:
                if not obj.workorder.status:
                    raise PermissionDenied(PromptMxins.require_handleable)
                if approve_user == user:
                    raise PermissionDenied(PromptMxins.require_different)
            elif uri in approve_perms:
                if approve_user != user:
                    raise PermissionDenied(PromptMxins.require_same)
        if uri in reject_perms:
            current_step = ActionMxins.get_current_step(obj)
            commiter = 'commiter_true' if obj.commiter == user.username else 'commiter_false'
            return self.parse_result(current_step in step_rules[role][commiter], PromptMxins.reject_warning)
        return self.check_perm(env, is_manual_review, role, uri)

    def check_perm(self, env, is_manual_review, role, uri):
        try:
            perm_obj = AuthRules.objects.get(env=env, is_manual_review=is_manual_review, role=role)
            perm_serializer = AuthRulesSerializer(perm_obj)
            return perm_serializer.data.get(uri)
        except Exception as e:
            return False
