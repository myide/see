# -*- coding:utf-8 -*-
from django.contrib.auth.models import Group, Permission
from collections import OrderedDict
from django.forms.models import model_to_dict
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(UserSerializer, self).to_representation(instance)
        if not isinstance(instance, OrderedDict):
            groupobj = instance.groups.first()
            groups = {'id':groupobj.id, 'name':groupobj.name} if groupobj else {}
            perm_list = instance.user_permissions.all()
            perms = [{'id':perm.id, 'name':perm.name} for perm in perm_list]
            ret['groups'] = groups
            ret['perms'] = perms
        return ret

    def create_sysaccount(self, validated_data):
        print(validated_data)
        sys_account = validated_data.pop('sysaccount',[])
        for account in sys_account:
            validated_data[account] = 1
        return validated_data

    def update_sysaccount(self, validated_data):
        default_account = {
            'is_active':0,
            'is_staff':0,
            'is_superuser':0
        }
        sys_account = validated_data.pop('sysaccount',[])
        for account in sys_account:
            if account in default_account:
                default_account[account] = 1
        validated_data.update(default_account)
        return validated_data

    def create(self, validated_data):
        instance = super(UserSerializer, self).create(self.create_sysaccount(validated_data))
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        print(validated_data)
        validated_data.pop('password')
        newpassword = validated_data.pop('newpassword')
        if newpassword:
            instance.set_password(newpassword)
        validated_data = self.update_sysaccount(validated_data)
        return super(UserSerializer, self).update(instance, validated_data)

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(GroupSerializer, self).to_representation(instance)
        if not isinstance(instance, OrderedDict):
            qs_perms = instance.permissions.all()
            perms = [{'id':perm.id, 'name':perm.name} for perm in qs_perms]
            qs_members = instance.user_set.all()
            members = [{'id':user.id, 'name':user.username, 'role':user.role} for user in qs_members]
            ret['perms'] = perms
            ret['members'] = members
        return ret

class PermissionSerializer(serializers.ModelSerializer):

    perm_name = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = '__all__'

    def get_perm_name(self, instance):
        return ' '.join((instance.content_type.app_label, instance.content_type.model, instance.name))

