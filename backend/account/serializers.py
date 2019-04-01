# -*- coding:utf-8 -*-
from django.contrib.auth.models import Group, Permission
from guardian.models import UserObjectPermission, GroupObjectPermission
from collections import OrderedDict
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from utils.basemixins import AppellationMixin, PromptMixin
from sqlmng.models import DbConf
from .models import User
from .mixins import SetPerm

class UserSerializer(AppellationMixin, PromptMixin, SetPerm, serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['user_permissions']

    def to_representation(self, instance):
        ret = super(UserSerializer, self).to_representation(instance)
        if not isinstance(instance, OrderedDict):
            group_instance = instance.groups.first()
            groups = {'id':group_instance.id, 'name':group_instance.name} if group_instance else {}
            ret['groups'] = groups
            ret['perms'] = self.get_perms(instance.userobjectpermission_set.all())
        return ret

    def check_permission(self, validated_data):
        update_able = False
        if not self.context:
            return
        user = self.context['request'].user
        if user.is_superuser:
            return
        validated_user = User.objects.get(id=validated_data.get('id'))
        role = user.role
        if role == self.dev_mng:
            if user != validated_user.leader:
                raise PermissionDenied(self.permission_leader.format(validated_user.username))
            return update_able
        if role == self.dev_spm:
            group = user.groups.first()
            if not group or group != validated_user.groups.first():
                raise PermissionDenied(self.permission_group.format(validated_user.username))
            return update_able
        if role == self.dev:
            raise PermissionDenied

    def create(self, validated_data):
        db_id_list = validated_data.pop('db_id_list', [])
        instance = super(UserSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        self.create_perm(instance, db_id_list, UserObjectPermission)
        return instance

    def update(self, instance, validated_data):
        update_able = self.check_permission(validated_data)
        db_id_list = validated_data.pop('db_id_list', None)
        password = validated_data.pop('password', None)
        if instance.password != password:
            instance.set_password(password)
        if db_id_list is not None:
            UserObjectPermission.objects.filter(user=instance).delete()
            self.create_perm(instance, db_id_list, UserObjectPermission)
        if update_able is False:
            return
        return super(UserSerializer, self).update(instance, validated_data)

class GroupSerializer(SetPerm, serializers.ModelSerializer):

    class Meta:
        model = Group
        exclude = ['permissions']

    def to_representation(self, instance):
        ret = super(GroupSerializer, self).to_representation(instance)
        if not isinstance(instance, OrderedDict):
            member_set = instance.user_set.all()
            members = [{'id':user.id, 'name':user.username, 'role':user.role} for user in member_set]
            ret['perms'] = self.get_perms(instance.groupobjectpermission_set.all())
            ret['members'] = members
        return ret

    def create(self, validated_data):
        db_id_list = validated_data.pop('db_id_list', [])
        instance = super(GroupSerializer, self).create(validated_data)
        instance.save()
        self.create_perm(instance, db_id_list, GroupObjectPermission)
        return instance

    def update(self, instance, validated_data):
        db_id_list = validated_data.pop('db_id_list', [])
        GroupObjectPermission.objects.filter(group=instance).delete()
        self.create_perm(instance, db_id_list, GroupObjectPermission)
        return super(GroupSerializer, self).update(instance, validated_data)

class PermissionSerializer(AppellationMixin, serializers.ModelSerializer):
    perm_name = serializers.SerializerMethodField()

    class Meta:
        model = DbConf
        fields = '__all__'

    def get_perm_name(self, instance):
        name = instance.cluster.name if instance.cluster else ''
        return ' | '.join((name, self.env_desc_map.get(instance.env), instance.name))

class PersonalCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password']
