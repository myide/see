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

    def create(self, validated_data):
        instance = super(UserSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if instance.password != password:
            instance.set_password(password)
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

class PersonalCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password']
