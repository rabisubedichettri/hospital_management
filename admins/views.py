from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .forms import AdminCheckForm,UserForm, DoctorForm,PatientRegistrationForm,DoctorAvailabilityDayForm,DoctorAvailabilityShiftForm,CustomFormTime
from django.contrib.auth.models import User
from doctor.models import Doctor
from patient.models import Patient
from django.contrib import messages
from appointment.models import DoctorAvailabilityDay,DoctorAvailabilityShift
import json
from django.utils import timezone
from appointment.models import Appointment
from hospital_management.views import role_required

def current_user(request):
    if request.user.is_authenticated:
        print("pass1")
        if request.user.is_superuser:
            print("pass2")
            return redirect("/")

   


# Create your views here.
@role_required(allowed_roles=['admin'])
def landing_page(request):
    return render(request,'admin/landing_page.html')

def login_(request):
    message = None
    form = AdminCheckForm(None)
    if request.method=="POST":
        form = AdminCheckForm(request.POST or None)
        print(form)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if not user:
                message = 'Wrong Credentials !!!'
            else:
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, 'You are logged in  as admin')
                    return redirect("/admin/dashboard/")

                    # redirect to admin_dashboard
                else:
                    message = 'You do not have enough credentials to login as admin'
        else:
            message = 'Authentication failed. Please provide your credentials.'
    
    return render(request, 'admin/landing_page.html', {'form': form, 'message': message})

@role_required(allowed_roles=['admin'])
def dashboard(request):
    # #for both table in admin dashboard
    doctors=Doctor.objects.all().order_by('-id')
    patients=Patient.objects.all().order_by('-id')
    # #for three cards
    doctorcount=doctors.filter(status=True).count()
    pendingdoctorcount=doctors.filter(status=False).count()

    patientcount=patients.filter(status=True).count()
    pendingpatientcount=patients.filter(status=False).count()

    # appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    # pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()

    # mydict={
    # 'doctors':doctors,
    # 'patients':patients,
    # 'doctorcount':doctorcount,
    # 'pendingdoctorcount':pendingdoctorcount,
    # 'patientcount':patientcount,
    # 'pendingpatientcount':pendingpatientcount,
    # 'appointmentcount':appointmentcount,
    # 'pendingappointmentcount':pendingappointmentcount,
    # }


    mydict={
        'doctors':doctors,
        'patients':patients,
        'doctorcount':doctorcount,
        'pendingdoctorcount':pendingdoctorcount,
        'patientcount':patientcount,
        'pendingpatientcount':pendingpatientcount,
    
    }
    return render(request,'admin/dashboard.html',context=mydict)


# admin-doctor related views
@role_required(allowed_roles=['admin'])
def admin_dash_doctor(request):
    if request.user.is_superuser:
        doctors=Doctor.objects.all()
        data={
            "total_doctors":doctors.count(),
            "active_doctors": doctors.filter(status=True).count(),
            "deactivate_doctors": doctors.filter(status=False).count(),
            'approve_doctors':doctors.filter(approve=True).count(),
            'disapprove_doctors':doctors.filter(approve=False).count(),

        }
        return render(request,'admin/doctor_view.html',data)
   

@role_required(allowed_roles=['admin'])
def get_all_doctors(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            username = request.GET.get('username')
            first_name=request.GET.get('first_name')
            last_name=request.GET.get('last_name')
            userid=request.GET.get('userid')
            address = request.GET.get('address')
            email = request.GET.get('email')
            status = request.GET.get('status','True')
            approve = request.GET.get('approve','True')
            experience = request.GET.get('experience')
            education = request.GET.get('education')
            department=request.GET.get('department')
            doctors=Doctor.objects.all()
            if username:
                doctors = doctors.filter(user__username__icontains=username)
            if first_name:
                doctors = doctors.filter(user__first_name__icontains=first_name)
            if last_name:
                doctors = doctors.filter(user__last_name__icontains=last_name)
            if userid:
                doctors = Doctor.objects.filter(user_id=userid)
            if address:
                doctors = Doctor.objects.filter(address=address)
            if email:
                doctors = doctors.filter(user__email__icontains=email)
            if experience:
                doctors = doctors.filter(experience__icontains=experience)
            if education:
                doctors = doctors.filter(education__icontains=education)
            if approve is not None and approve in ['True', 'False']:
                doctors = doctors.filter(approve=approve)
            if status is not None and status in ['True', 'False']:
                doctors = doctors.filter(status=status)
            if department:
                doctors = doctors.filter(department=department)
        return render(request,'admin/doctor_all.html',{'doctors':doctors,'data':locals()})
    else:
        return redirect("/admin/login")

@role_required(allowed_roles=['admin'])
def get_doctor_detail(request, doctor_id):
    if request.user.is_superuser:
        try:
            doctor = Doctor.objects.get(user__id=doctor_id)
        except Doctor.DoesNotExist:
            return HttpResponse("Doctor does not exist", status=404)
            
        if request.method=="POST":
            action = request.POST.get('action')
            find_action= action in ['activate', 'deactivate','approve','disapprove','delete']
            if action is not None and find_action:
                if action=="activate":
                    doctor.status=True
                    messages.success(request, 'Activated successfully Username:{}'.format(doctor.user.username))
                elif action=="deactivate":
                    doctor.status=False
                    messages.warning(request,'Dectivated successfully Username:{}'.format(doctor.user.username))
                elif action=="disapprove":
                    doctor.approve=False
                    messages.warning(request,'Disapproved successfully Username:{}'.format(doctor.user.username))
                elif action=='approve':
                    doctor.approve=True
                    messages.success(request, 'Approved successfully Username:{}'.format(doctor.user.username))
                else:
                    print("dddddddd")
                    # remove doctor 
                    username=doctor.user.username
                    doctor.delete()
                    messages.success(request, 'deleted successfully Username:{}'.format(username))
                    return redirect("/")
                doctor.save()
                
        return render(request, 'admin/doctor_detail.html', {'doctor': doctor})

@role_required(allowed_roles=['admin'])
def update_doctor(request,id):
    if request.user.is_superuser:
        pass
    else:
        return redirect("/admin/login")

@role_required(allowed_roles=['admin'])
def register_doctor(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            user_form = UserForm(request.POST)
            doctor_form = DoctorForm(request.POST, request.FILES)
            
            if user_form.is_valid() and doctor_form.is_valid():
                user = user_form.save()
                doctor = doctor_form.save(commit=False)
                doctor.user = user
                doctor.save()
                user_form = UserForm()
                doctor_form = DoctorForm()
                messages.success(request, 'Registered successfully Username:{}'.format(doctor.user.username))
                
        else:
            user_form = UserForm()
            doctor_form = DoctorForm()
        
        return render(request, 'admin/register_doctor.html', {'user_form': user_form, 'doctor_form': doctor_form})
    else:
        return redirect("/admin/login")

#  patient start

# admin-patient related views
@role_required(allowed_roles=['admin'])
def admin_dash_patient(request):
    if request.user.is_superuser:
        patients=Patient.objects.all()
        data={
            "total_patients":patients.count(),
            "active_patients":patients.filter(status=True).count(),
            "deactivate_patients": patients.filter(status=False).count(),
            'approve_patients':patients.filter(approve=True).count(),
            'disapprove_patients':patients.filter(approve=False).count(),

        }
        return render(request,'admin/patient_view.html',data)
    else:
        return redirect("/admin/login")

@role_required(allowed_roles=['admin'])
def register_patient(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            user_form = UserForm(request.POST)
            patient_form = PatientRegistrationForm(request.POST, request.FILES)
            
            if user_form.is_valid() and patient_form.is_valid():
                user = user_form.save()
                patient =patient_form.save(commit=False)
                patient.user = user
                patient.save()
                user_form = UserForm()
                patient_form = PatientRegistrationForm()
                messages.success(request, 'Registered successfully Username:{}'.format(patient.user.username))
                
        else:
            user_form = UserForm()
            patient_form = PatientRegistrationForm()
        return render(request,"admin/register_patient.html",{'user_form': user_form, 'patient_form': patient_form})

    else:
        return redirect("/admin/login")

@role_required(allowed_roles=['admin'])
def get_all_patients(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            username = request.GET.get('username')
            first_name=request.GET.get('first_name')
            last_name=request.GET.get('last_name')
            userid=request.GET.get('userid')
            address = request.GET.get('address')
            email = request.GET.get('email')
            status = request.GET.get('status','True')
            approve = request.GET.get('approve','True')
            patients=Patient.objects.all()
            if username:
                patients = patients.filter(user__username__icontains=username)
            if first_name:
                patients = patients.filter(user__first_name__icontains=first_name)
            if last_name:
                patients = patients.filter(user__last_name__icontains=last_name)
            if userid:
                patients = patients.filter(user_id=userid)
            if address:
                patients = patients.filter(address=address)
            if email:
                patients = patients.filter(user__email__icontains=email)
            if approve is not None and approve in ['True', 'False']:
                patients = patients.filter(approve=approve)
            if status is not None and status in ['True', 'False']:
                patients = patients.filter(status=status)

        return render(request,'admin/patient_all.html',{'patients':patients,'data':locals()})
    else:
        return redirect("/admin/login")

@role_required(allowed_roles=['admin'])
def get_patient_detail(request, doctor_id):
    if request.user.is_superuser:
        try:
            patient = Patient.objects.get(user__id=doctor_id)
        except Patient.DoesNotExist:
            return HttpResponse("Patient does not exist", status=404)
            
        if request.method=="POST":
            action = request.POST.get('action')
            find_action= action in ['activate', 'deactivate','approve','disapprove','delete']
            if action is not None and find_action:
                if action=="activate":
                    patient.status=True
                    messages.success(request, 'Activated successfully Username:{}'.format(patient.user.username))
                elif action=="deactivate":
                    patient.status=False
                    messages.warning(request,'Dectivated successfully Username:{}'.format(patient.user.username))
                elif action=="disapprove":
                    doctor.approve=False
                    messages.warning(request,'Disapproved successfully Username:{}'.format(patient.user.username))
                elif action=='approve':
                    patient.approve=True
                    messages.success(request, 'Approved successfully Username:{}'.format(patient.user.username))
                else:
                    username=patient.user.username
                    patient.delete()
                    messages.success(request, 'deleted successfully Username:{}'.format(username))
                    return redirect("/")
                patient.save()
                
        return render(request, 'admin/patient_detail.html', {'patient': patient})

# admin-appointment related views
@role_required(allowed_roles=['admin'])
def admin_dash_appointment(request):
    doctors_with_availability = Doctor.objects.filter(doctoravailabilityday__isnull=False).distinct()
    doctor_availability = {}
    total_appointment_day = 0  # Initialize count for total appointment days
    for doctor in doctors_with_availability:
        availability_days = list(DoctorAvailabilityDay.objects.filter(doctor=doctor).values_list('available_day', flat=True))
        doctor_availability[doctor.user.first_name + " " + doctor.user.last_name] = availability_days
        total_appointment_day += len(availability_days)  # Increment total appointment days
    data = json.dumps(doctor_availability, default=str)
    return render(request, 'admin/dash_appointment.html', {'data': data, 'total_appointment_day': total_appointment_day})

@role_required(allowed_roles=['admin'])
def admin_create_appointment(request):
    
    if request.user.is_superuser:
        if request.method == 'POST':
            form = DoctorAvailabilityDayForm(request.POST)
            if form.is_valid():
                instance=form.save()
                messages.success(request, 'Appointment created')
                return redirect('/admin/dashboard/appointment/shfit/{}'.format(instance.id))  # Redirect to a success URL
        else:
            
            form = DoctorAvailabilityDayForm()
        doctors=Doctor.objects.all()
        return render(request, 'admin/create_appointment.html', {'doctors':doctors,'form': form})


@role_required(allowed_roles=['admin'])
def admin_create_shift(request,appointment_day):
    availability_day = get_object_or_404(DoctorAvailabilityDay, id=appointment_day)
    doc_ava_shift=DoctorAvailabilityShift.objects.filter(doctor_availability_day=availability_day)

    if request.method == 'POST':
        form = CustomFormTime(request.POST)
        action = request.POST.get('action',"")
        if action =="remove":
            available_shift_id=request.POST.get('available_shift',"")
            print(available_shift_id)
            if  available_shift_id is not None:
                available_shift = get_object_or_404(DoctorAvailabilityShift, id=available_shift_id)
                available_shift.delete()
                messages.success(request,"shift deleted")
        else:
            if form.is_valid():
                shift=DoctorAvailabilityShift()
                shift.doctor_availability_day=availability_day
                shift.start_time=form.cleaned_data['start_time']
                shift.end_time=form.cleaned_data['end_time']
                shift.save()
                messages.success(request,"added time shift")
                return redirect('/admin/dashboard/appointment/shfit/{}/'.format(availability_day.id))  # Redirect to a success URL
    else:
        # Pass the DoctorAvailabilityDay instance to the form as initial data
        form = DoctorAvailabilityShiftForm(initial={'doctor_availability_day': availability_day})
    context={'doctor_available_shifts':doc_ava_shift,'form': form,'data':availability_day}
    return render(request, 'admin/create_shift.html', context)
    

@role_required(allowed_roles=['admin'])
def get_available_days(request):
    if request.user.is_superuser:
        if request.method=="POST":
            delete_day=request.POST.get('delete_day')
            print(delete_day)
            if delete_day is not None:
                obj=DoctorAvailabilityDay.objects.get(id=delete_day)
                obj.delete()
                messages.success(request,'deleted successfully doctor availability day')


        doctors_with_availability = Doctor.objects.filter(doctoravailabilityday__isnull=False).distinct()
        doctor_availability = {}
        for doctor in doctors_with_availability:
            doctor_availability[doctor] = DoctorAvailabilityDay.objects.filter(doctor=doctor)
        return render(request, 'admin/available_days.html', {'doctor_availability': doctor_availability})


@role_required(allowed_roles=['admin'])
def appointment_taken(request):
# Get the current date and time (timezone-aware)
    current_datetime = timezone.now()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(finished=True)

    patient_info = []

    for appointment in appointments:
        # Extract patient information from the appointment
        patient = {
            'appointment_id':appointment.id,
            'patient_name': appointment.patient.user.get_full_name(),
            'doctor_name':appointment.available_shift.doctor_availability_day.doctor.user.get_full_name(),
            'appointment_date': appointment.available_shift.doctor_availability_day.doctor.user.get_full_name(),
            'start_time': appointment.available_shift.start_time,
            'end_time': appointment.available_shift.end_time,
        }

        patient_info.append(patient)

    return render(request, 'admin/taken.html', {"info":patient_info})

@role_required(allowed_roles=['admin'])
def appointment_onging(request):
# Get the current date and time (timezone-aware)
    current_datetime = timezone.localtime()

    # Filter appointments for the current doctor user, unfinished, and with appointment date greater than or equal to today's date
    appointments = Appointment.objects.filter(
        finished=False,
        available_shift__doctor_availability_day__available_day__gte=current_datetime.date()
    )

    running_appointments = []

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
            info = {
                'appointment_id': appointment.id,
                'patient_name': appointment.patient.user.get_full_name(),
                'appointment_date': appointment.available_shift.doctor_availability_day.available_day,
                'start_time': appointment.available_shift.start_time,
                'end_time': appointment.available_shift.end_time,
                'doctor_name':appointment.available_shift.doctor_availability_day.doctor.user.get_full_name(),
            }
            running_appointments.append(info)
        

    return render(request, 'admin/ongoing.html', {"data":running_appointments})



@role_required(allowed_roles=['admin'])
def notification(request):
    return render(request,"admin/notification.html")
    
@role_required(allowed_roles=['admin'])
def chat(request):
    return render(request,"admin/chat.html")