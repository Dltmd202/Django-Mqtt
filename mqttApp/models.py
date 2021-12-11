from django.db import models


# Create your models here.
class Lock(models.Model):
    degree = models.FloatField()


class Window(models.Model):
    degree = models.FloatField()


class Information(models.Model):
    distance = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    is_person = models.BooleanField(default=False)
    is_rain = models.BooleanField(default=False)


class Home(models.Model):
    time = models.DateTimeField(auto_now=True)
    information = models.ForeignKey(Information, on_delete=models.CASCADE)
    lock = models.OneToOneField(Lock, on_delete=models.CASCADE)
    window = models.OneToOneField(Window, on_delete=models.CASCADE)