# -*- coding: utf-8 -*-
from django.conf.urls import url
from.views import SqlFileView

urlpatterns = [
    url(r'^download/sqlhandle/(?P<pk>\d+).(?P<sfx>\w+)$', SqlFileView.as_view())
]