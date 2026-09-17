import os
import django
from django.core.asgi import get_asgi_application

# 1. Primeiro define o módulo de configurações
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'EducaFamilly.settings'
)

# 2. Inicializa o Django antes de qualquer import de app
django.setup()
django_asgi_app = get_asgi_application()

# 3. Agora sim importa as rotas e os websockets
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from chat.presence_routing import websocket_urlpatterns as presence_websocket_urlpatterns

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