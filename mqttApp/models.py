from django.db import models


# Create your models here.
class temp(models.Model):
    time = models.DateTimeField(auto_now=True)
    temp = models.FloatField()
    humidity = models.FloatField()


class distance(models.Model):
    time = models.DateTimeField(auto_now=True)
    distance = models.FloatField()


class detect(models.Model):
    time = models.DateTimeField(auto_now=True)
    is_human = models.BooleanField(default=False)


class moter(models.Model):
    degree = models.FloatField()