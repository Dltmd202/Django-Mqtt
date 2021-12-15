from django.urls import path
from . import views

urlpatterns = [
    path("inf/<int:pk>/", views.InformationDetail.as_view()),
    path("inf/<int:pk>/open/", views.openRequest),
    path("inf/<int:pk>/close/", views.closeRequest),
    path("inf/<int:pk>/<str:wt>/<str:wh>/", views.adjustTempHum)
]
