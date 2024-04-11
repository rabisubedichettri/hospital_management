from django.shortcuts import render,HttpResponseRedirect,redirect,get_object_or_404
from . import forms
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .models import Patient
from .forms import PatientUserForm,PatientForm
from admins.forms import UserForm
from doctor.models import Doctor
from appointment.models import DoctorAvailabilityDay,DoctorAvailabilityShift,Appointment,Prescribe
from admins.forms import DoctorAvailabilityShiftForm
from appointment.forms import AppointmentForm
from django.db.models import Exists,Subquery
from django.db import models
import json
from django.utils import timezone
from datetime import datetime
from hospital_management.views import role_required
from notification.models import Notification

from admins.forms import CustomPasswordChangeForm

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.
@role_required(allowed_roles=['patient'])
def landing_page(request):
    if request.user.is_authenticated:
        pass
    return render(request,'hospital/patientclick.html')


def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        patient_form = PatientForm(request.POST, request.FILES)
        print(user_form)
        print(patient_form)
        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save()
            patient =patient_form.save(commit=False)
            patient.user = user
            patient.save()
    
            return redirect('/patient/login')
            # messages.success(request, 'Registered successfully Username:{}'.format(patient.user.username))
    else:
        user_form = UserForm()
        patient_form = PatientForm()
            
    return render(request,"patient/register.html",{'user_form': user_form, 'patient_form': patient_form})

def login_(request):

    message = None
    if request.method=="POST":
        form = forms.PatientLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if not user:
                message = 'Wrong Credentials !!!'
            else:
                patient = Patient.objects.filter(user=user).first()
                if patient:
                    login(request, user)
                    messages.success(request, 'You are logged in  as patient')
                    return redirect("/patient/dashboard")

                    # redirect to admin_dashboard
                else:
                    message = 'You do not have enough credentials to login as patient'
        else:
            message = 'Authentication failed. Please provide your credentials.'
    
    return render(request,"patient/login.html",{'message':message})

@role_required(allowed_roles=['patient'])
def dashboard(request):
    data={
        "total_appoinment_taken":get_total_appointment_taken(request),
        'total_upcoming_appointment':get_total_appoinment_upcoming(request),
    }
    return render(request,"patient/dashboard.html",data)


@role_required(allowed_roles=['patient'])
def get_available_days(request):
    doctors_with_availability = Doctor.objects.filter(
        doctoravailabilityday__isnull=False,
        doctoravailabilityday__doctoravailabilityshift__isnull=False
    ).distinct()

    doctor_availability = {}
    for doctor in doctors_with_availability:
        availability_days = DoctorAvailabilityDay.objects.filter(doctor=doctor)
        doctor_shifts = {}
        for day in availability_days:
            shifts = DoctorAvailabilityShift.objects.filter(doctor_availability_day=day)
            available_shifts = shifts.filter(start_time__isnull=False, end_time__isnull=False,reserved=False)
            doctor_shifts[day] = available_shifts
        doctor_availability[doctor] = available_shifts
    return render(request, 'patient/available_days.html', {'doctor_availability': doctor_availability})


@role_required(allowed_roles=['patient'])
def find_shift(request,appointment_day):
    availability_day = get_object_or_404(DoctorAvailabilityDay, id=appointment_day)
    doc_ava_shift=DoctorAvailabilityShift.objects.filter(doctor_availability_day=availability_day)

        # Pass the DoctorAvailabilityDay instance to the form as initial data
    context={'doctor_available_shifts':doc_ava_shift,'data':availability_day}
    return render(request, 'admin/create_shift.html', context)


@role_required(allowed_roles=['admin'])
def take_shift(request,appointment_day): #unmamnged
    availability_day = get_object_or_404(DoctorAvailabilityDay, id=appointment_day)
    doc_ava_shift=DoctorAvailabilityShift.objects.filter(doctor_availability_day=availability_day,reserved=False)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            available_shift_id=request.POST.get('available_shift_id',"")
            title=form.cleaned_data['title']
            symptoms=form.cleaned_data['symptoms']

            # also check the shift is reserved or not
            shift_obj=DoctorAvailabilityShift.objects.get(id=available_shift_id,reserved=False)
            patient_obj = Patient.objects.get(user__id=request.user.id)
            appoint_obj=Appointment(
                    available_shift =shift_obj,
                    patient=patient_obj,
                    finished = False,
                    title=title,
                    symptoms=symptoms
                    )
            appoint_obj.save()
            shift_obj.reserved=True
            shift_obj.save()
            messages.success(request,"appointment taken")

            return redirect("/")
        print(form)

    else:
        form = DoctorAvailabilityShiftForm(initial={'doctor_availability_day': availability_day})
    context={'doctor_available_shifts':doc_ava_shift,'form': form,'data':availability_day}
    return render(request, 'patient/take_shift.html', context)

@role_required(allowed_roles=['patient'])
def appointment_taken(request):
        # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        patient__user=request.user,
        finished=True,
    )

    patient_info = []

    for appointment in appointments:
        # Extract patient information from the appointment
        patient = {
            'appointment_id':appointment.id,
            'doctor': appointment.available_shift.doctor_availability_day.doctor,
            'appointment_date': appointment.available_shift.doctor_availability_day.available_day,
            'start_time': appointment.available_shift.start_time,
            'end_time': appointment.available_shift.end_time,
            'title': appointment.title,
            'symptoms': appointment.symptoms,
        }

        patient_info.append(patient)

    return render(request, 'patient/appointment_taken.html', {"info":patient_info})

@role_required(allowed_roles=['patient'])
def appointment_upcoming(request):
    # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        patient=Patient.objects.get(user=request.user),
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )

    doctor_availability = {}
    doctor_availability_info = []
    total_appointment = 0  # Initialize count for total appointment days

    for appointment in appointments:
        # Get the availability day and start time for the appointment
        availability_day = appointment.available_shift.doctor_availability_day.available_day
        start_time = appointment.available_shift.start_time

        # If the availability day is today's date, check the appointment time
        if availability_day == current_datetime.date():
            # Convert the start time to a datetime object for comparison
            appointment_datetime = datetime.combine(availability_day, start_time)

            # Check if the appointment time is greater than the current time
            print(appointment_datetime)
            print(current_datetime)
            if timezone.make_aware(appointment_datetime, timezone.get_current_timezone()) > current_datetime:
                # Add availability day to the dictionary
                doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
                if doctor_name not in doctor_availability:
                    doctor_availability[doctor_name] = []

                doctor_availability[doctor_name].append(availability_day)
                doctor_availability_info.append(appointment)
                total_appointment += 1  # Increment total appointment days
        else:
            # Add availability day to the dictionary
            doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
            if doctor_name not in doctor_availability:
                doctor_availability[doctor_name] = []

            doctor_availability[doctor_name].append(availability_day)
            doctor_availability_info.append(appointment)
            total_appointment += 1  # Increment total appointment days
            
    info = doctor_availability
    data = json.dumps(doctor_availability, default=str)
    return render(request, 'patient/upcoming.html', {'data': data, 'total_appointment_day': total_appointment, 'info': doctor_availability_info})

@role_required(allowed_roles=['patient'])
def appointment_view(request,id):
    appointment=Appointment.objects.get(id=id)
    prescribe=Prescribe.objects.filter(appointment__id=id)
    data={}
    if prescribe.exists():
        data["prescribe"]=prescribe
    data["appoinment"]=appointment
    data['doctor']=data["appoinment"].available_shift.doctor_availability_day.doctor
    
    return render(request,"patient/appointment_view.html",data)

@role_required(allowed_roles=['patient'])
def notification(request):
    notifications=Notification.objects.filter(recipient=request.user)
    return render(request,"patient/notification.html",{"notifications":notifications})

@role_required(allowed_roles=['patient'])
def profile(request):
    patient=Patient.objects.get(user=request.user)
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request,"Password Changed successfully")
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request,"patient/profile.html",{"patient":patient,"form":form})


def get_total_appointment_taken(request):
    # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        patient=Patient.objects.get(user=request.user),
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )

    doctor_availability = {}
    doctor_availability_info = []
    total_appointment = 0  # Initialize count for total appointment days

    for appointment in appointments:
        # Get the availability day and start time for the appointment
        availability_day = appointment.available_shift.doctor_availability_day.available_day
        start_time = appointment.available_shift.start_time

        # If the availability day is today's date, check the appointment time
        if availability_day == current_datetime.date():
            # Convert the start time to a datetime object for comparison
            appointment_datetime = datetime.combine(availability_day, start_time)

            # Check if the appointment time is greater than the current time
            print(appointment_datetime)
            print(current_datetime)
            if timezone.make_aware(appointment_datetime, timezone.get_current_timezone()) > current_datetime:
                # Add availability day to the dictionary
                doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
                if doctor_name not in doctor_availability:
                    doctor_availability[doctor_name] = []

                doctor_availability[doctor_name].append(availability_day)
                doctor_availability_info.append(appointment)
                total_appointment += 1  # Increment total appointment days
        else:
            # Add availability day to the dictionary
            doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
            if doctor_name not in doctor_availability:
                doctor_availability[doctor_name] = []

            doctor_availability[doctor_name].append(availability_day)
            doctor_availability_info.append(appointment)
            total_appointment += 1  # Increment total appointment days
    return total_appointment
    
def get_total_appoinment_upcoming(request):
    # Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        patient=Patient.objects.get(user=request.user),
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )

    doctor_availability = {}
    doctor_availability_info = []
    total_appointment = 0  # Initialize count for total appointment days

    for appointment in appointments:
        # Get the availability day and start time for the appointment
        availability_day = appointment.available_shift.doctor_availability_day.available_day
        start_time = appointment.available_shift.start_time

        # If the availability day is today's date, check the appointment time
        if availability_day == current_datetime.date():
            # Convert the start time to a datetime object for comparison
            appointment_datetime = datetime.combine(availability_day, start_time)

            # Check if the appointment time is greater than the current time
            print(appointment_datetime)
            print(current_datetime)
            if timezone.make_aware(appointment_datetime, timezone.get_current_timezone()) > current_datetime:
                # Add availability day to the dictionary
                doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
                if doctor_name not in doctor_availability:
                    doctor_availability[doctor_name] = []

                doctor_availability[doctor_name].append(availability_day)
                doctor_availability_info.append(appointment)
                total_appointment += 1  # Increment total appointment days
        else:
            # Add availability day to the dictionary
            doctor_name = f"{appointment.available_shift.doctor_availability_day.doctor.user.first_name} {appointment.available_shift.doctor_availability_day.doctor.user.last_name}"
            if doctor_name not in doctor_availability:
                doctor_availability[doctor_name] = []

            doctor_availability[doctor_name].append(availability_day)
            doctor_availability_info.append(appointment)
            total_appointment += 1  # Increment total appointment days
            
    info = doctor_availability
    return len(info)