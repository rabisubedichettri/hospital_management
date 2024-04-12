from django.shortcuts import render,HttpResponseRedirect,redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps
from doctor.models import Doctor
from django.contrib.auth import logout
from patient.models import Patient
from chat.models import AnonymousRoom,AnonymousRoomMessage

# views.py
from django.contrib.auth.views import PasswordResetView
from .forms import CustomPasswordResetForm


def home(request):
    user_ip = request.META.get('REMOTE_ADDR',"")
    room_name=None
    chat_data=None
    if not request.user.is_authenticated:
        check_anonymous=AnonymousRoom.objects.filter(ip_address=user_ip)
        if check_anonymous.exists():
            room_name=check_anonymous[0]
        else:
            room_name=AnonymousRoom(ip_address=user_ip)
            room_name.save()
        chat_data=AnonymousRoomMessage.objects.filter(room=room_name)
        room_name=room_name.room_name

    return render(request,'home.html',{'room_name':room_name,"chat_data":chat_data})


def about_us(request):
    return render(request,'hospital/aboutus.html')

def contact_us(request):
    sub=None
    return render(request, 'hospital/contactus.html', {'form':sub})


def logout_(request):
    logout(request)
    messages.success(request, 'You are logged out successfully.')
    return redirect("/")

def register(request):
    pass


# Decorator for role-based access control
def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # if not request.user.is_authenticated:
            #     return redirect('/')  # Redirect to login if user is not authenticated
            
            
            if 'admin' in allowed_roles:
                if not request.user.is_authenticated:
                    return redirect("/admin/login")
                else:
                    if not request.user.is_superuser:
                        logout(request)
                        messages.success(request,"logged out and you are redirected to admin login")
                        return redirect("/admin/login")
            
            if 'patient' in allowed_roles:
                if not request.user.is_authenticated:
                    return redirect("/patient/login")
                else:
                    doctor_obj=Doctor.objects.filter(user=request.user)
                    if doctor_obj.exists() or request.user.is_superuser:
                        logout(request)
                        messages.success("logged out and you are redirected to patient login")
                        return redirect("/patient/login")

            if 'doctor' in allowed_roles:
                if not request.user.is_authenticated:
                    return redirect("/doctor/login")
                else:
                    patient_obj=Patient.objects.filter(user=request.user)
                    if patient_obj.exists() or request.user.is_superuser:
                        logout(request)
                        messages.success(request,"logged out and you are redirected to doctor login")
                        return redirect("/doctor/login")

            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator






class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
