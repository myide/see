# -*- coding:utf-8 -*-
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from utils.basemixins import AppellationMixin, PromptMixin, SetEncryptMixin
from .mixins import HandleInceptionSettingsMixin, PermissionDatabases
from .models import *

class BaseInceptionSerializer(PromptMixin, serializers.ModelSerializer):
    admin = 'Admin'

    class Meta:
        model = InceptionWorkOrder
        fields = '__all__'

    def get_step_user_group(self, user_instance):
        if not user_instance:
            return self.admin
        group_instance = user_instance.groups.first()
        return group_instance.name if group_instance else user_instance.username

    def get_step(self, instance):
        data = []
        steps = instance.work_order.step_set.order_by('id')
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
        ret = super(BaseInceptionSerializer, self).to_representation(instance)
        db = instance.db
        ret['db_name'] = db.name if db else ''
        cluster = db.cluster
        ret['cluster'] = cluster.name if cluster else ''
        ret['steps'] = self.get_step(instance)
        return ret

class DetailInceptionSerializer(BaseInceptionSerializer):
    pass

class ListInceptionSerializer(BaseInceptionSerializer):

    class Meta:
        model = InceptionWorkOrder
        exclude = ('handle_result', 'handle_result_check', 'handle_result_execute', 'handle_result_rollback')

class DbSerializer(SetEncryptMixin, serializers.ModelSerializer):

    class Meta:
        model = DbConf
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(DbSerializer, self).to_representation(instance)
        cluster = instance.cluster
        ret['cluster'] = {'id':cluster.id, 'name':cluster.name} if cluster else {}
        return ret

class SqlSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SqlSettings
        fields = '__all__'

class StrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = Strategy
        fields = '__all__'

class PersonalSerializer(AppellationMixin, PermissionDatabases, serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'

    def get_commiter(self, instance):
        return {'id':instance.id, 'username':instance.username}

    def get_leader(self, env, instance):
        leader_instance = instance.leader if env == self.env_prd else instance
        leader = {'id':leader_instance.id, 'username':leader_instance.username} if leader_instance else {}
        return leader

    def get_db_list(self, instance):
        db_queryset = self.filter_databases(instance.dbconf_set.all(), instance)
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

class InceptionVariablesSerializer(HandleInceptionSettingsMixin, serializers.ModelSerializer):

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

class DbWorkOrderSerializer(PromptMixin, serializers.ModelSerializer):

    class Meta:
        model = DatabaseWorkOrder
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(DbWorkOrderSerializer, self).to_representation(instance)
        ret['commiter'] = instance.commiter.username
        ret['treater'] = instance.treater.username
        return ret

    def create(self, validated_data):
        request = self.context['request']
        admin_mail = request.user.admin_mail
        if not admin_mail:
            raise ParseError(self.not_exists_admin_mail)
        validated_data.setdefault('commiter_id', request.user.id)
        validated_data.setdefault('treater_id', admin_mail.id)
        instance = super(DbWorkOrderSerializer, self).create(validated_data)
        instance.save()
        return instance
