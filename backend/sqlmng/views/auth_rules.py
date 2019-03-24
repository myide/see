# -*- coding: utf-8 -*-
from utils.baseviews import BaseView
from sqlmng.serializers import *
from sqlmng.data import auth_rules
from sqlmng.mixins import FixedDataMixin

class AuthRulesViewSet(FixedDataMixin, BaseView):
    '''
        平台权限
    '''
    serializer_class = AuthRulesSerializer
    search_fields = ['env']
    source_data = auth_rules