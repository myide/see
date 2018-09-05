#coding=utf8
from rest_framework import permissions
from sqlmng.models import *
from utils.basemixins import AppellationMixins

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
approve_perms = ['approve', 'disapprove']
handle_perms = ['execute', 'rollback']

class AuthOrReadOnly(AppellationMixins, permissions.BasePermission):

    def __init__(self):
        # 权限名
        self.reject_perms = ['reject']

    @property
    def get_permission(self):
        '''
        根据系统是否有审批流程，对不同人员授权（审批工单权限，执行SQL权限）
        :return:
        '''
        if Strategy.objects.first().is_manual_review:
            auths = {
                self.dev: self.reject_perms,
                self.dev_mng: self.reject_perms + approve_perms,
                self.dev_spm: self.reject_perms + approve_perms,
            }
        else:
            auths = {
                self.dev: self.reject_perms,
                self.dev_mng: self.reject_perms + handle_perms,
                self.dev_spm: self.reject_perms + handle_perms,
            }
        return auths

    def has_permission(self, request, view):
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if uri not in handle_perms + approve_perms:  # 非动作的操作（查询类的）
            return True
        pk = uri_list[-3]
        sqlobj = Inceptsql.objects.get(pk = pk)
        if sqlobj.env == self.env_test:  # 测试环境
            return True
        return uri in self.get_permission[request.user.role] or request.user.is_superuser  # 用户的身份有操作权限 or 是超级用户
        # return sqlobj.treater == request.user.username or request.user.is_superuser  # SQL的执行人是用户 or 是超级用户

class IsHandleAble(AppellationMixins, permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
            在调get_object()时检查该权限（get_object -- check_object_permissions -- has_object_permission）
        """
        print(obj)
        #if obj.env == self.env_test or obj.is_manual_review == False:
         #   return True
        user_id = request.user.id  # 当前访问者
        if obj.is_manual_review == True:
            approve_step_instance = obj.step_set.all()[1]
            approve_user_id = approve_step_instance.user.id  # 工单审批人
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if uri in handle_perms:  # 执行/回滚的检查项
            if obj.is_manual_review == False:
                return True
            else:
                if user_id == approve_user_id:  # 最终执行人与审批人，不能是同一人
                    return False
                return True if obj.handleable else False # 检查工单是否审批通过
        if uri in approve_perms:  # 审批的检查项
            if obj.env == self.env_test or obj.is_manual_review == False:  # 测试环境或没有审批流的生产环境，无审批权限
                return False
            if user_id != approve_user_id:  # 审批人和当前操作人，必须是同一人
                return False
        return True

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
