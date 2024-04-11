from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
# import  views
from . import views as root_view
from django.contrib.auth import views as auth_views

# home view / landig page
urlpatterns =  [
     path("chat/", include("chat.urls")),
    path("",root_view.home,name="home"),
    path("about-us/",root_view.about_us,name='about_us'),
    path("contact-us/",root_view.contact_us,name="contact_us"),
]

# Authentication and registration urls
urlpatterns+=[
    path("logout/",root_view.logout_,name="logout"),
    path("register/",root_view.register,name="register"),
    path("forget/",root_view.CustomPasswordResetView.as_view(),name="forget"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="rest_password_done.html"), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),

]


# Django default apps's url
urlpatterns+= [
    path('superuser/', admin.site.urls), # django default admin panel
]

# Local apps's urls
urlpatterns+=[
    path("admin/", include("admins.urls", namespace="admins")),  # for custom admin panel
    path("doctor/", include("doctor.urls", namespace="doctor")),  
    path("patient/", include("patient.urls", namespace="patient")),  
    path("payment/", include("payment.urls", namespace="payment")),
    path("notification/",include("notification.urls",namespace="notification")),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
