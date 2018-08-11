# -*- coding:utf-8 -*-
from rest_framework import serializers
from rest_framework.utils import model_meta
from .models import *
from utils.dbcrypt import prpcrypt

class InceptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inceptsql
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(InceptionSerializer, self).to_representation(instance)
        ret['db_name'] = instance.db.name
        return ret

class DbSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dbconf
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.get('password')
        pc = prpcrypt()
        validated_data['password'] = pc.encrypt(password)
        return super(DbSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password != instance.password:
            pc = prpcrypt()
            validated_data['password'] = pc.encrypt(password)
        return super(DbSerializer, self).update(instance, validated_data)
