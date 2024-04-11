# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[0-9a-f-]+)/$", consumers.AnonymousConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<room_name>[\w-]+)/$", consumers.AdminConsumer.as_asgi()),
]