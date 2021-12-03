from django.shortcuts import render
from rest_framework import generics
from mqttApp.models import Information
from mqttApp.serializers import InformationSerializer
# Create your views here.


class InformationDetail(generics.RetrieveUpdateAPIView):
    queryset = Information
    serializer_class = InformationSerializer
