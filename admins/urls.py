from django.urls import path

from django.contrib.auth.views import LoginView,LogoutView
from . import views

# App Name
app_name = "admins"

urlpatterns = [
    # admin home page before login
    path("",views.dashboard,name="landing_page"),
    path("notification/",views.notification,name="notification"),
    path("chat/",views.chat,name="chat"),

    #login
    path('login/', views.login_,name="login"),
    
    # admin home page after login
    path("dashboard/",views.dashboard,name="dashboard"),

    # doctor
    path("dashboard/doctor/",views.admin_dash_doctor,name='dashboard-doctor'),
    path("dashboard/doctor/view/",views.get_all_doctors,name="all-doctor-view"),
    path("dashboard/doctor/detail/<int:doctor_id>/",views.get_doctor_detail,name="get-doctor-detail"),
    path("dashboard/doctor/register/",views.register_doctor,name="register-doctor"),



    # patient
    path("dashboard/patient/",views.admin_dash_patient,name='dashboard-patient'),
    path("dashboard/patient/view/",views.get_all_patients,name="all-patient-view"),
    path("dashboard/patient/detail/<int:doctor_id>/",views.get_patient_detail,name="get-patient-detail"),
    path("dashboard/patient/register/",views.register_patient,name="register-doctor"),

    #appointment
    path("dashboard/appointment/",views.admin_dash_appointment,name="dashboard-appointment"),
    path("dashboard/appointment/create",views.admin_create_appointment,name="dashboard-appointment-create"),
    path("dashboard/appointment/available_days/",views.get_available_days,name="get_avilable_days"),
    path("dashboard/appointment/shfit/<int:appointment_day>/",views.admin_create_shift,name="appointment-shift"),
    path("dashboard/appointment/taken/",views.appointment_taken,name="appointment_taken"),
    path("dashboard/appointment/ongoing/",views.appointment_onging,name="appointment_ongoing"),
    
]