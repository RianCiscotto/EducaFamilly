
from django.urls import path

from .presence_consumers import PresenceConsumer


websocket_urlpatterns = [
    path(
        "ws/presence/",
        PresenceConsumer.as_asgi(),
    ),
]

