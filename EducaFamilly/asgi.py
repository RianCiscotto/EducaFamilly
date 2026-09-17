
import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from chat.presence_routing import websocket_urlpatterns as presence_websocket_urlpatterns


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'EducaFamilly.settings'
)


django_asgi_app = get_asgi_application()


websocket_urlpatterns = (
    presence_websocket_urlpatterns
    + chat_websocket_urlpatterns
)


application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(

        URLRouter(
            websocket_urlpatterns
        )

    ),

})

