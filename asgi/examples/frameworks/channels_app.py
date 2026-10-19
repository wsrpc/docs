import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.http import JsonResponse
from django.urls import path
from wsrpc_asgi import WebSocketAsync


def create_handler():
    class RPC(WebSocketAsync):
        pass

    async def echo(socket, **params):
        return params

    async def callback(socket, *, value):
        return await socket.proxy.double(value=value)

    RPC.add_route("echo", echo)
    RPC.add_route("callback", callback)
    return RPC


# In an existing project keep DJANGO_SETTINGS_MODULE and its settings.
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="local-example-only",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
    )
django.setup()


def health(request):
    return JsonResponse({"ok": True})


urlpatterns = [path("health", health)]
http_app = get_asgi_application()
rpc = create_handler().as_asgi()
app = ProtocolTypeRouter(
    {
        "http": http_app,
        "websocket": URLRouter([path("ws/", rpc)]),
    }
)
