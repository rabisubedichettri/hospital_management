from django import forms
from .models import Appointment,Prescribe

class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = ('title', 'symptoms')


class PrescribeForm(forms.ModelForm):
    class Meta:
        model=Prescribe
        fields=('text',)