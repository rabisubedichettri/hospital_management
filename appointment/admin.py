from django.contrib import admin

# Register your models here.
from .models import DoctorAvailabilityDay,DoctorAvailabilityShift,Appointment
admin.site.register(DoctorAvailabilityDay)
admin.site.register(DoctorAvailabilityShift)
admin.site.register(Appointment)
