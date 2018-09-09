#coding=utf8
from utils.baseviews import BaseView
from sqlmng.serializers import *
from sqlmng.models import *

class StepViewSet(BaseView):
    '''
        工单审批流
    '''
    queryset = Step.objects.all()
    serializer_class = StepSerializer