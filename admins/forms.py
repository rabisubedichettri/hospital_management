from django import forms

# forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from doctor.models import Doctor, DEPARTMENTS
from appointment.models import DoctorAvailabilityDay,DoctorAvailabilityShift
from patient.models import Patient
from datetime import datetime, timedelta


class AdminCheckForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)  # Make first name required
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.', required=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

class DoctorForm(forms.ModelForm):
    department = forms.ChoiceField(choices=DEPARTMENTS)

    class Meta:
        model = Doctor
        fields = ('profile_pic', 'address', 'mobile', 'department', 'email', 'experience', 'details')

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model= Patient
        fields=('profile_pic', 'address', 'mobile')




class DoctorAvailabilityDayForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailabilityDay
        fields = ['doctor', 'available_day',]


class DoctorAvailabilityShiftForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailabilityShift
        fields = ['doctor_availability_day', 'start_time', 'end_time', 'reserved']



class CustomTimeField(forms.TimeField):
    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            parsed_time = datetime.strptime(value.upper(), '%I:%M%p')
        except ValueError:
            raise forms.ValidationError('Enter a valid time.')

        return parsed_time.time()



class CustomFormTime(forms.Form):
    start_time = CustomTimeField(label='Custom Time')
    end_time = CustomTimeField(label='Custom Time')