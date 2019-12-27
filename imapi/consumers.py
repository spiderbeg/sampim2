from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # 数据库操作
from django.db.models import Q
import json

from im.models import UserMessage, GroupMessage, UserRelation, Group, GroupUser, UserProfile, SaveImage
from imapi.serializer import UserMessageSerializer, GroupMessageSerializer, UserSerializer, SaveImageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # async 关键字 将生成器转化为 协程 类型
        self.room_group_name = 'chat_im'
        await database_sync_to_async(self.online_log)('login') # 修改登录状态
        # join room group
        # await 关键字
        # 1 执行 await 右边方法，返回产出值 如 a = await a()
        # 2 同时 connecct() 阻塞
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
        # 登录时，通知群组
        # 向 group 发送信息
        await self.channel_layer.group_send(
            self.room_group_name, # group name
            {
                'type': 'chat_message',
                'receiver': 'receiver',
                'sender': 'sender',
                'gptype': 'group',
            }
        )


    async def disconnect(self, close_code):
        await database_sync_to_async(self.online_log)('logout') # 修改登录状态
        # 退出登录时，通知 group
        # 向 group 发送信息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'receiver': 'receiver',
                'sender': 'sender',
                'gptype': 'group',
            }
        )
        # 离开群组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        
    
    # 接收来自 Websocket 的消息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print('question',text_data_json)
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
        gptype = text_data_json['gp']
        # 异步调用数据库
        # newest = await database_sync_to_async(self.create_log)()
        # print('user ??: ', vars(self.scope["user"]), self.scope["user"].username)

        # 向 group 发送信息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'receiver': receiver,
                'sender': sender,
                'gptype': gptype,
            }
        )
    
    # 接收来自 group 的信息
    async def chat_message(self, event):
        gptype = event['gptype']
        sender = event['sender']
        receiver = event['receiver']   
        # send = await database_sync_to_async(self.check_send)(gptype,sender,receiver)
        send = self.check_send(gptype,sender,receiver)

        # 向 WebSocket 发送消息
        if send:
            await self.send(text_data=json.dumps({
                'message': 'new message',
            }))

    def check_send(self, gptyle, sender, receiver):
        """决定是否向相关客户端推送信息"""
        if sender == 'personal' and self.scope["user"].username not in [sender, receiver]:
            return False
        return True

    def online_log(self, type):
        """修改用户登录状态"""
        status, _= UserProfile.objects.get_or_create(user=self.scope["user"])
        status.online = True if type == 'login' else False
        status.save()
        