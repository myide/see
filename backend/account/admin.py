# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import User
from django.contrib import admin

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'remark',
    )

admin.site.register(User, UserAdmin)
