# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'permissions', PermissionViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'users', UserViewSet)
router.register(r'personal', PersonalCenterViewSet, base_name='PersonalCenterViewSet')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^unitaryauth/$', UnitaryAuthView.as_view())
]
