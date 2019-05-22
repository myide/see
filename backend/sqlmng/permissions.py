# -*- coding: utf-8 -*-
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from utils.permissions import SAFE_METHODS
from utils.basemixins import HttpMixin, AppellationMixin, PromptMixin
from sqlmng.serializers import AuthRulesSerializer
from sqlmng.models import *

reject_perms = ['reject']
approve_perms = ['approve', 'disapprove']
handle_perms = ['execute', 'rollback', 'cron']

class IsHandleAble(HttpMixin, AppellationMixin, permissions.BasePermission):

    def parse_result(self, has_auth, desc):
        if not has_auth:
            raise PermissionDenied(desc)
        return True

    def get_approve_user(self, obj):
        approve_step_instance = obj.work_order.step_set.order_by('id')[1]
        return approve_step_instance.user

    def has_object_permission(self, request, view, obj):
        user = request.user
        env = obj.env
        is_manual_review = obj.is_manual_review
        role = self.admin if user.is_superuser else user.role
        action = self.get_urls_action(request)
        if (request.method in SAFE_METHODS and action not in reject_perms + approve_perms + handle_perms) or env == self.env_test:
            return True
        if obj.is_manual_review is True:
            approve_user = self.get_approve_user(obj)
            if action in handle_perms:
                if not obj.work_order.status:
                    raise PermissionDenied(PromptMixin.require_handleable)
                if approve_user == user:
                    raise PermissionDenied(PromptMixin.require_different)
            elif action in approve_perms:
                if approve_user != user and role != self.dev_spm:
                    raise PermissionDenied(PromptMixin.require_same)
        return self.check_perm(env, is_manual_review, role, action)

    def check_perm(self, env, is_manual_review, role, action):
        try:
            perm_obj = AuthRules.objects.get(env=env, is_manual_review=is_manual_review, role=role)
            perm_serializer = AuthRulesSerializer(perm_obj)
            return perm_serializer.data.get(action)
        except Exception as e:
            print(e)
            return False
