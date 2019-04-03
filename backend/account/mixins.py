# -*- coding: utf-8 -*-
from django.conf import settings
from sqlmng.models import DbConf

class SetPerm(object):

    perm = settings.PERM_DATABASE

    def get_perms(self, perm_list):
        perms = []
        for perm in perm_list:
            db_instance = DbConf.objects.filter(pk=perm.object_pk)
            if db_instance:
                item = {
                    'id': int(perm.object_pk),
                    'name': db_instance[0].name
                }
                perms.append(item)
        return perms

    def create_perm(self, instance, db_id_list, user_group):
        for db_id in db_id_list:
            obj = DbConf.objects.get(id=db_id)
            user_group.objects.assign_perm(self.perm, instance, obj=obj)
