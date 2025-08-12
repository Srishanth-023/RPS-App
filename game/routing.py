# game/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # e_path(r'ws/game/$', consumers.GameConsumer.as_asgi()),
]