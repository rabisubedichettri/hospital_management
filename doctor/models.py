from django.db import models

# Create your models here.
from django.contrib.auth.models import User

DEPARTMENTS = [
    ('Cardiologist','Cardiologist'),
    ('Dermatologists','Dermatologists'),
    ('Emergency Medicine Specialists','Emergency Medicine Specialists'),
    ('Allergists/Immunologists','Allergists/Immunologists'),
    ('Anesthesiologists','Anesthesiologists'),
    ('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
    ]

GENDER = [
    ('Male','Male'),
    ('Female','Female'),
    ]

class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='media/profile_pic/DoctorProfilePic/')
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    department= models.CharField(max_length=50,choices=DEPARTMENTS,default='Cardiologist')
    status=models.BooleanField(default=False)
    approve=models.BooleanField(default=False)
    education=models.CharField(max_length=40)
    email=models.EmailField(max_length=250)
    experience=models.CharField(max_length=34)
    details=models.TextField(max_length=2000)
    license_id=models.CharField(max_length=34)
    gender=models.CharField(max_length=50,choices=GENDER,default='Male')
    
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)

# class Prescribe(models.Model):
#     patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
#     doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prescribed_by")
#     given = models.BooleanField(default=False)
#     updated_at = models.DateTimeField(auto_now=True)
#     text = models.TextField()
