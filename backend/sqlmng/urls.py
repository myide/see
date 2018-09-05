#coding=utf-8
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .views.inception_check import InceptionCheckView
from .views.select_data import SelectDataView
from .views.settings import ForbiddenWordsViewSet, StrategyViewSet, PersonalSettingsViewSet
from .views.step import StepViewSet
from .views.target_db import DbViewSet
from .views.workorder_main import InceptionMainView

# register的可选参数 base_name: 用来生成urls名字，如果viewset中没有包含queryset, base_name一定要有

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
