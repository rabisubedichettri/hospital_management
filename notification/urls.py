from django.urls import path

from . import views

# App Name
app_name = "notification"


urlpatterns = [
    path("",views.notification,name="notification"),
   
    
]