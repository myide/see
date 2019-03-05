# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework import status
from utils.baseviews import BaseView
from sqlmng.serializers import *
from sqlmng.models import *

class SuggestionViewSet(BaseView):
    '''
        工单意见评论
    '''
    serializer_class = SuggestionSerializer

    def get_queryset(self):
        work_order_id = self.request.GET.get('work_order_id')
        return Suggestion.objects.filter(work_order_id = work_order_id)

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
