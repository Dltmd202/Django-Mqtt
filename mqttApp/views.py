from django.shortcuts import render
from rest_framework import generics
from mqttApp.models import Information
from mqttApp.serializers import InformationSerializer
import paho.mqtt.client as mqtt
from mqttApp.userSensor import UserSensor

from django.http import JsonResponse
# Create your views here.


class InformationDetail(generics.RetrieveUpdateAPIView):
    queryset = Information
    serializer_class = InformationSerializer


def openRequest(request, pk):
    user = UserSensor()
    user.run(True)
    msg = {
        "success": True
    }
    return JsonResponse(msg)


def closeRequest(request, pk):
    user = UserSensor()
    user.run(False)
    msg = {
        "success": True
    }
    return JsonResponse(msg)
