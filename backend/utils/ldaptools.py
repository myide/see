# -*- coding: utf-8 -*-
import ldap
from django.conf import settings

class LdapSee(object):

    locals().update(settings.LDAP)
    ret = {}

    def check(self, ldap_user, ldap_password):
        uri = "ldap://{}:{}".format(self.host, self.port)
        conn = ldap.initialize(uri)
        try:
            conn.simple_bind_s(ldap_user, ldap_password)
            status = 0
        except ldap.INVALID_CREDENTIALS:
            status = -1
        except Exception as e:
            status = -2
            self.ret["data"] = e
        self.ret["status"] = status
        return self.ret
