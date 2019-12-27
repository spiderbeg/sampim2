# 连接到引用 consumer.py 的路由配置
from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    path('ws/total/', consumers.ChatConsumer),
]
