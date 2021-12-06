from django.urls import path
from . import views

urlpatterns = [
    path("inf/<int:pk>/", views.InformationDetail.as_view()),
]
