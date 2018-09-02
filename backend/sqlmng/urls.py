#coding=utf-8
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'dbconfs', DbViewSet, base_name='DbViewSet')
router.register(r'inceptions', InceptionMainView, base_name='InceptionMainView')
router.register(r'inceptioncheck', InceptionCheckView, base_name='InceptionCheckView')
router.register(r'autoselects', SelectDataView, base_name='SelectDataView')
router.register(r'forbiddenwords', ForbiddenWordsViewSet, base_name='ForbiddenWordsViewSet')
router.register(r'strategy', StrategyViewSet, base_name='StrategyViewSet')
router.register(r'personalsettings', PersonalSettingsViewSet, base_name='PersonalSettingsViewSet')

urlpatterns = [
    url(r'^', include(router.urls)),
]
