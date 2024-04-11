from django.shortcuts import render,HttpResponseRedirect,redirect
from . import forms
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import Doctor
from admins.forms import UserForm,DoctorForm
from django.utils import timezone
from patient.models import Patient
from appointment.models import Appointment,Prescribe
import json
from appointment.forms import PrescribeForm
from hospital_management.views import role_required
# Create your views here.
def landing_page(request):
    if request.user.is_authenticated:
        pass
    return render(request,'hospital/doctorclick.html')


def login_(request):
    message = None
    if request.method=="POST":
        form = forms.DoctorLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if not user:
                message = 'Wrong Credentials !!!'
            else:
                doctor = Doctor.objects.filter(user=user).first()
                if doctor:
                    login(request, user)
                    messages.success(request, 'You are logged in  as doctor')
                    return redirect("/doctor/dashboard")

                    # redirect to admin_dashboard
                else:
                    message = 'You do not have enough credentials to login as doctor'
        else:
            message = 'Authentication failed. Please provide your credentials.'
    
    return render(request,"doctor/login.html",{'message':message})

def register(request): #done
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        
        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save()
            doctor =doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
    
            return redirect('/doctor/login')
            # messages.success(request, 'Registered successfully Username:{}'.format(patient.user.username))
    else:
        user_form = UserForm()
        doctor_form = DoctorForm()
            
    return render(request,"doctor/register.html",{'user_form': user_form, 'doctor_form': doctor_form})


@role_required(allowed_roles=['doctor'])
def dashboard(request):
    mydict={}
    return render(request,'doctor/dashboard.html',context=mydict)

@role_required(allowed_roles=['doctor'])
def appointment_upcoming(request):
    # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        available_shift__doctor_availability_day__doctor__user=request.user,
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )

    patient_info = []

    for appointment in appointments:
        # Extract patient information from the appointment
        patient = {
            'appointment_id':appointment.id,
            'patient_name': appointment.patient.user.get_full_name(),
            'appointment_date': appointment.available_shift.doctor_availability_day.available_day,
            'start_time': appointment.available_shift.start_time,
            'end_time': appointment.available_shift.end_time,
            'title': appointment.title,
            'symptoms': appointment.symptoms,
        }

        patient_info.append(patient)

    data = json.dumps(patient_info, default=str)
    return render(request, 'doctor/upcoming.html', {'data': data,"info":patient_info})

@role_required(allowed_roles=['doctor'])
def live_monitor(request):
    patient={}
    if request.user.is_authenticated:
        if request.method=="POST":
            id=request.POST.get('id',"")
            if id is not None:
                form = PrescribeForm(request.POST)
                if form.is_valid():
                    text=form.cleaned_data['text']

                    prescribe=Prescribe()
                    prescribe.text=text
                    prescribe.doctor=Doctor.objects.get(user=request.user)
                # get appointment obj
                appointment=Appointment.objects.get(id=id)
                prescribe.appointment= appointment
                prescribe.save()
                messages.success(request,"Prescription given")
                appointment.finished=True
                appointment.save()
                return redirect("/")



    # Get the current date and time (timezone-aware)
    current_datetime = timezone.localtime()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        available_shift__doctor_availability_day__doctor__user=request.user,
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )
    print(appointments)

    running_appointments = []
    start_datetime=None

    for appointment in appointments:
    # Check if the appointment is currently running
        start_datetime = timezone.make_aware(timezone.datetime.combine(appointment.available_shift.doctor_availability_day.available_day, appointment.available_shift.start_time))
        end_datetime = timezone.make_aware(timezone.datetime.combine(appointment.available_shift.doctor_availability_day.available_day, appointment.available_shift.end_time))
        print(start_datetime)
        print(current_datetime)
        print(end_datetime)
        if start_datetime <= current_datetime<=end_datetime:
            remaining_time = end_datetime - current_datetime
        
            # Extract patient information from the appointment
            patient = {
                'appointment_id': appointment.id,
                'patient_name': appointment.patient.user.get_full_name(),
                'appointment_date': appointment.available_shift.doctor_availability_day.available_day,
                'start_time': appointment.available_shift.start_time,
                'end_time': appointment.available_shift.end_time,
                'title': appointment.title,
                'symptoms': appointment.symptoms,
                 'remaining_time': remaining_time.total_seconds()/60 ,
            }

            print(patient)
        

    # data = json.dumps(running_appointments, default=str)
    return render(request, 'doctor/live_monitor.html', {'patient': patient,"refresh_time":start_datetime})

@role_required(allowed_roles=['doctor'])
def appointment_taken(request):
    # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        available_shift__doctor_availability_day__doctor__user=request.user,
        finished=True,
    )

    patient_info = []

    for appointment in appointments:
        # Extract patient information from the appointment
        patient = {
            'appointment_id':appointment.id,
            'patient_name': appointment.patient.user.get_full_name(),
            'appointment_date': appointment.available_shift.doctor_availability_day.available_day,
            'start_time': appointment.available_shift.start_time,
            'end_time': appointment.available_shift.end_time,
            'title': appointment.title,
            'symptoms': appointment.symptoms,
        }

        patient_info.append(patient)

    return render(request, 'doctor/taken.html', {"info":patient_info})

role_required(allowed_roles=['doctor'])
def appointment_view(request,id):
    appointment=Appointment.objects.get(id=id)
    prescribe=Prescribe.objects.filter(appointment__id=id)
    data={}
    if prescribe.exists():
        data["prescribe"]=prescribe
    data["appoinment"]=appointment
    return render(request,"doctor/appointment_view.html",data)

role_required(allowed_roles=['doctor'])
def notification(request):
    return render(request,"doctor/notification.html")