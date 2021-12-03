from mqttApp.models import Information

from rest_framework import serializers


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'

