"""
ASGI config for djangops project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""



import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangops.settings')
django.setup()
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import easyops.consumers
from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from whitenoise import WhiteNoise
# import easyops.routing

# application = get_asgi_application() 

# application = WhiteNoise(application, root='/data/django/djangops/static')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r'ws/easyops/(?P<room_name>\w+)/$',
                easyops.consumers.ChatConsumer.as_asgi()),
            url(r'ws/avcheck/(?P<ac_id>\w+)/$',
                easyops.consumers.AcConsumer.as_asgi()),
            # easyops.routing.websocket_urlpatterns
        ])
    ),
    "channel": ChannelNameRouter({
        "c0": easyops.consumers.ChatConsumer.as_asgi(),
        "c1": easyops.consumers.ChatConsumer.as_asgi(),
        "c2": easyops.consumers.ChatConsumer.as_asgi(),
        "c3": easyops.consumers.ChatConsumer.as_asgi(),
        "c4": easyops.consumers.ChatConsumer.as_asgi(),
        "c5": easyops.consumers.AcConsumer.as_asgi(),
        "c6": easyops.consumers.AcConsumer.as_asgi(),
        "c7": easyops.consumers.AcConsumer.as_asgi(),
        "c8": easyops.consumers.AcConsumer.as_asgi(),
        "c9": easyops.consumers.AcConsumer.as_asgi(),
    }),
})
