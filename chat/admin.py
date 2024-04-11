from django.contrib import admin
from .models import AnonymousRoom,AnonymousRoomMessage
# Register your models here.
admin.site.register(AnonymousRoom)
admin.site.register(AnonymousRoomMessage)