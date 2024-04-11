# chat/urls.py
from django.urls import path

from . import views
app_name="chat"
urlpatterns = [
    path("", views.index, name="index"),
      path("<uuid:room_uuid>/", views.room, name="room"),
]