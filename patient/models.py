from django.db import models
# Create your models here.
from django.contrib.auth.models import User

# Create your models here.

class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/PatientProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    status=models.BooleanField(default=False)
    approve=models.BooleanField(default=False)

    # symptoms = models.CharField(max_length=100,null=False)
    # assignedDoctorId = models.PositiveIntegerField(null=True)
    # admitDate=models.DateField(auto_now=True)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name+" ("+self.symptoms+")"

