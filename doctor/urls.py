from django.urls import path

from . import views

# App Name
app_name = "doctor"


urlpatterns = [
    path("",views.landing_page,name="landing_page"),
    path("profile/",views.profile,name='profile'),
    path("login/",views.login_,name="login"),
    path("register/",views.register,name="register"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("appointment/upcoming/",views.appointment_upcoming,name="upcoming"),
    path("appointment/taken/",views.appointment_taken,name="taken"),
    path("appointment/live/",views.live_monitor,name="live monitor"),
    path("appointment/<int:id>/",views.appointment_view,name="appointment_view"),
    path("notification/",views.notification,name="notification"),
    
]