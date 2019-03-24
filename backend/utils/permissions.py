# -*- coding: utf-8 -*-
from rest_framework import permissions

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
