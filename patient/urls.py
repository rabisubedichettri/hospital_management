from django.urls import path

from . import views

# App Name
app_name = "patient"

urlpatterns = [
    path("",views.landing_page,name="landing_page"),
    path("profile/",views.profile,name="profile"),
    path("login/",views.login_,name="login"),
    path("register/",views.register,name="register"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("available_days/",views.get_available_days,name="_get_available_days"),
    path("take/shift/<int:appointment_day>/",views.take_shift,name="take_shift"),
    path("appointment/upcoming/",views.appointment_upcoming,name="appointment_upcoming"),
    path("appointment/taken/",views.appointment_taken,name="appointment_taken"),
    path("appointment/<int:id>/",views.appointment_view,name="appointment_view"),
    path("notification/",views.notification,name="notification"),

]

