# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from django.http import StreamingHttpResponse
from utils.basemixins import PromptMixin

class RenderFile(object):
    path = settings.MEDIA.get('sql_file_path')

    def create_file(self, params, content):
        pk, sfx = params.get('pk'), params.get('sfx')
        file_name = '{}.{}'.format(pk, sfx)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        path = os.path.join(self.path, file_name)
        with open(path, 'w') as f:
            content_list = json.loads(content)
            length = len(content_list)
            if isinstance(content_list, list):
                for row in content_list:
                    f.write(str(row))
                    if content_list.index(row) < length - 1:
                        f.write('\n')
            else:
                f.write(content)
        return path, file_name

    def file_iterator(self, file_path, chunk_size=512):
        with open(file_path) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

class DownloadBaseView(PromptMixin, RenderFile, APIView):

    def check_content(self):
        content = self.get_content()
        if not content:
            raise ParseError(self.get_content_fail)
        return content

    def get(self, request, *args, **kwargs):
        content = self.check_content()
        file_path, file_name = self.create_file(kwargs, content)
        response = StreamingHttpResponse(self.file_iterator(file_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        return response
