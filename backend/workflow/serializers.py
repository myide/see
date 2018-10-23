from rest_framework import serializers
from .models import Workorder, Step

class WorkorderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workorder
        fields = '__all__'

class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = '__all__'
