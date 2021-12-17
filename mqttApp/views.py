import os

from django.shortcuts import render
from rest_framework import generics
from mqttApp.models import Information
from mqttApp.serializers import InformationSerializer
import paho.mqtt.client as mqtt
from mqttApp.userSensor import UserSensor

from django.http import JsonResponse

from .models import Information
import requests

# Create your views here.


class InformationDetail(generics.RetrieveUpdateAPIView):
    queryset = Information
    serializer_class = InformationSerializer


def openRequest(request, pk):
    user = UserSensor()
    mqttMsg = {
        "order": True
    }
    user.run(mqttMsg)
    msg = {
        "success": True
    }
    info = Information.objects.get(pk=pk)
    info.is_open = True
    info.save()
    return JsonResponse(msg)


def closeRequest(request, pk):
    user = UserSensor(topic="sensor/user")
    mqttMsg = {
        "order": False
    }
    user.run(mqttMsg)
    msg = {
        "success": True
    }
    info = Information.objects.get(pk=pk)
    info.is_open = False
    info.save()
    return JsonResponse(msg)


def adjustTempHum(request, pk, wt, wh):
    if request.method == 'GET':
        information = Information.objects.get(pk=pk)
        information.wishing_temp = float(wt)
        information.wishing_hum = float(wh)
        information.save()
        user = UserSensor(topic="sensor/wish")
        mqttMsg = {
            "wishTemperature": float(wt),
            "wishHum": float(wh)
        }
        user.run(mqttMsg)
        msg = {
            "success": True
        }
        return JsonResponse(msg)
