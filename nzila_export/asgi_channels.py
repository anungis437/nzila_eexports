"""
ASGI config for nzila_export project.

This module contains the ASGI application used for WebSocket support via Django Channels.
It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
https://channels.readthedocs.io/en/stable/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')

# Initialize Django ASGI application early to ensure apps are loaded
django_asgi_app = get_asgi_application()

# Import routing after Django initialization
from chat import routing as chat_routing

application = ProtocolTypeRouter({
    # HTTP protocol (standard Django)
    "http": django_asgi_app,
    
    # WebSocket protocol (Django Channels)
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat_routing.websocket_urlpatterns
            )
        )
    ),
})
