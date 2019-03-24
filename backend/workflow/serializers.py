# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import WorkOrder, Step

class WorkOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkOrder
        fields = '__all__'

class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = '__all__'
