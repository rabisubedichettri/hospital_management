from django.db import models
from patient.models import Patient

class Admission(models.Model):
    GENDER_CHOICES = (
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
    )

    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    symptoms = models.TextField(max_length=2000)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    discharge = models.BooleanField(default=False)

    def __str__(self):
        return f"Admission for {self.patient} ({self.start_date} to {self.end_date})"


class AdmissionBill(models.Model):
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE)
    bill_num = models.CharField(max_length=100)
    bill_title = models.CharField(max_length=100)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Bill for {self.admission.patient} - {self.bill_title}"