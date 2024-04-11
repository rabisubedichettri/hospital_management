from django.db import models
# Create your models here.
from django.contrib.auth.models import User

# Create your models here.

class Appointment(models.Model):
    patient=models.PositiveIntegerField(null=True)
    doctor=models.PositiveIntegerField(null=True)
    date=models.DateField(auto_now=True)  
    description=models.TextField(max_length=500)
    status=models.BooleanField(default=False)
    symptoms = models.CharField(max_length=100,null=False)
    date=models.DateField(auto_now=True)

    
