# -*- coding:utf-8 -*-
from rest_framework import serializers
from utils.basemixins import AppellationMixins, SetEncryptMixins
from .mixins import HandleInceptionSettingsMixins
from .models import *

class InceptionSerializer(serializers.ModelSerializer):

    admin = 'Admin'
    class Meta:
        model = Inceptsql
        fields = '__all__'

    def get_step_user_group(self, user_instance):
        group_name = user_instance.groups.first().name if user_instance and not user_instance.is_superuser else self.admin
        return group_name

    def get_step(self, instance):
        data = []
        steps = instance.workorder.step_set.order_by('id')
        for step in steps:
            username = step.user.username if step.user else self.admin
            updatetime = step.updatetime if step.status != 0 else ''
            group = self.get_step_user_group(step.user)
            data.append(
                {
                    'id': step.id,
                    'updatetime': updatetime,
                    'username': username,
                    'group':group,
                    'status':step.status
                }
            )
        data.insert(0, {'updatetime':instance.createtime, 'username':'Inception', 'group':'自动审核', 'status':1})
        return data

    def to_representation(self, instance):
        ret = super(InceptionSerializer, self).to_representation(instance)
        ret['db_name'] = instance.db.name
        ret['steps'] = self.get_step(instance)
        return ret

class DbSerializer(SetEncryptMixins, serializers.ModelSerializer):

    class Meta:
        model = Dbconf
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(DbSerializer, self).to_representation(instance)
        cluster = instance.cluster
        ret['cluster'] = {'id':cluster.id, 'name':cluster.name} if cluster else {}
        return ret

class ForbiddenWordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ForbiddenWords
        fields = '__all__'

class StrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = Strategy
        fields = '__all__'

class PersonalSerializer(AppellationMixins, serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'

    def get_commiter(self, instance):
        return {'id':instance.id, 'username':instance.username}

    def get_leader(self, env, instance):
        leader_obj = instance.leader if env == self.env_prd else instance
        leader = {'id':leader_obj.id, 'username':leader_obj.username} if leader_obj else {}
        return leader

    def get_db_list(self, instance):
        db_queryset = instance.dbconf_set.all()
        db_list = []
        if db_queryset:
            for db in db_queryset:
                cluster = db.cluster
                if not cluster:continue
                cluster_id = cluster.id
                cluster_name = cluster.name
                row = {
                    'id': db.id,
                    'name': db.name,
                    'env': db.env,
                    'cluster_id': cluster_id,
                    'cluster_name': cluster_name,
                }
                db_list.append(row)
        return db_list

    def to_representation(self, instance):
        env = self.context['request'].GET.get('env')
        ret = super(PersonalSerializer, self).to_representation(instance)
        ret['leader'] = self.get_leader(env, instance)
        ret['db_list'] = self.get_db_list(instance)
        ret['commiter'] = self.get_commiter(instance)
        return ret

class AuthRulesSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthRules
        fields = '__all__'

class SuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Suggestion
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(SuggestionSerializer, self).to_representation(instance)
        ret['username'] = instance.user.username if instance.user else ''
        return ret

class DbClusterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cluster
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(DbClusterSerializer, self).to_representation(instance)
        ret['dbs'] = [db.id for db in instance.dbconf_set.all()]
        return ret

class InceptionVariablesSerializer(HandleInceptionSettingsMixins, serializers.ModelSerializer):

    class Meta:
        model = InceptionVariables
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(InceptionVariablesSerializer, self).to_representation(instance)
        ret['value'] = self.get_status(instance.name)
        return ret

class InceptionConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InceptionConnection
        fields = '__all__'

class MailActionsSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MailActions
        fields = '__all__'