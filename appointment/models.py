from django.db import models
from patient.models import Patient
from doctor.models import Doctor
# Create your models here.
class DoctorAvailabilityDay(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    available_day = models.DateField()
    reserved=models.BooleanField(default=False)
    active=models.BooleanField(default=False)

class DoctorAvailabilityShift(models.Model):
    doctor_availability_day=models.ForeignKey(DoctorAvailabilityDay,on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    reserved=models.BooleanField(default=False)

class Appointment(models.Model):
    available_shift = models.ForeignKey(DoctorAvailabilityShift, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    title = models.CharField(max_length=50,null=True)
    symptoms = models.TextField(max_length=2000,null=True)

class Prescribe(models.Model):
    appointment=models.ForeignKey(Appointment,on_delete=models.CASCADE)
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    text=models.TextField(max_length=2000)
    


class AppointmentBill(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    bill_amount = models.CharField(max_length=100)
    paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField()


