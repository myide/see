# -*- coding: utf-8 -*-
from django.conf import settings
from sqlmng.models import DbConf

class SetPerm(object):

    perm = settings.PERM_DATABASE

    def get_perms(self, perm_list):
        perms = [{'id': int(perm.object_pk), 'name': DbConf.objects.get(pk=perm.object_pk).name} for perm in perm_list]
        return perms

    def create_perm(self, instance, db_id_list, user_group):
        for db_id in db_id_list:
            obj = DbConf.objects.get(id=db_id)
            user_group.objects.assign_perm(self.perm, instance, obj=obj)
