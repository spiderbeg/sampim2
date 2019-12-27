from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import imapi.routing 

application = ProtocolTypeRouter({
    # (http->Django views is add by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            imapi.routing.websocket_urlpatterns
        )
    )
})