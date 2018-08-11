#coding=utf8
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

class ReturnFormatMixin(object):
    ret = {'status': 0, 'msg': '', 'data': {}}

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pagesize'
    page_query_param = 'page'
    max_page_size = 1000

class BaseView(ReturnFormatMixin, viewsets.ModelViewSet):
    queryset = None
    serializer_class = None
    permission_classes = []
    # 分页
    pagination_class = DefaultPagination
    # 搜索
    filter_backends = [filters.SearchFilter]
    search_fields = []

    def perform_create(self, serializer):
        serializer.create(self.request.data)

    def perform_update(self, serializer):
        serializer.update(self.get_object(), self.request.data)
