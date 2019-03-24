# -*- coding: utf-8 -*-
from sqlmng.models import InceptionWorkOrder
from .mixins import DownloadBaseView

class SqlFileView(DownloadBaseView):
    '''
        文件下载
    '''
    model = InceptionWorkOrder

    def get_content(self):
        pk = self.kwargs.get('pk')
        data_type = self.request.GET.get('data_type')
        instance = self.model.objects.get(pk=pk)
        content = getattr(instance, data_type)
        return content
