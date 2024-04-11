import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import AnonymousRoom, AnonymousRoomMessage
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

class AnonymousConsumer(AsyncWebsocketConsumer):

    async def check_anonymous_room(self):
        return await database_sync_to_async(
            AnonymousRoom.objects.filter(room_name=self.room_group_name).exists
        )()

    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]

        user = self.scope['user']
        if not user.is_authenticated:
            check_anonymous = await self.check_anonymous_room()
            print(check_anonymous)
            if not check_anonymous:
                await self.close()
                return
        else:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("anynomous",text_data_json)

        action = text_data_json.get("action", False)
        if action == 'send.message':
            # format={
            #     'action':'send.message',
            #     'message':message,
                 
            # }
            message = text_data_json.get("message", None)
            receiver=text_data_json.get("sender", None)
            if message and receiver:


                await self.create_message(message,receiver)
                #calling code: 1111
                await self.channel_layer.group_send(
                    'admin',
                    {
                        "type": "sendto.admin",
                        "message": message,
                        "receiver":receiver,
                    }
                    )
               

        if action == "type.message":
            # format={
            #     'action':'type.message',
            # }
            # called code: 2222
            receiver=text_data_json.get("sender", None)
            if receiver:
    

                await self.channel_layer.group_send('admin',
                {"type": "typeto.admin",
                "receiver":receiver,
                })

    # called code: 3333
    # this method is called when anynomous user send a message
    # got by admin
    async def sendto_anynomous(self, event):
        await self.send(text_data=json.dumps({
            "action": "got.message",
            "receiver":event['receiver'],
            "message":event["message"],
            }))

    # called code: 4444
    # this method is called when anynomous user type a message
    # got by admin
    async def typeto_anynomous(self,event):
        await self.send(text_data=json.dumps({
            "action": "typed.message",
            }))
    
    async def create_message(self, message,receiver):
        room, found = await self.get_room(receiver)
        if not found:
            return
        await database_sync_to_async(AnonymousRoomMessage.objects.create)(
            room=room,
            message=message,
            sender_type='ANONYMOUS',  
            sent_time=timezone.now(),
            read=False
        )


    async def get_room(self, receiver):
        try:
            room = await database_sync_to_async(AnonymousRoom.objects.get)(room_name=receiver)
            found = True
        except AnonymousRoom.DoesNotExist:
            room = None
            found = False  # Set created to False since the room wasn't created
        return room, found

    

class AdminConsumer(AsyncWebsocketConsumer):

    # called code: 1111
    # this method is called when anynomous user send a message
    # got by admin
    async def sendto_admin(self, event):
        await self.send(text_data=json.dumps({
            "action": "got.message",
            "message":event['message'],
            "receiver":event['receiver']
            }))

    # called code: 222
    # this method is called when anynomous user type a message
    # got by admin
    async def typeto_admin(self,event):
        await self.send(text_data=json.dumps({
            "action": "typed.message",
            "receiver":event['receiver'],
            }))
  
    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        if not self.room_group_name == "admin":
            self.close()
            return

        if self.room_group_name=="admin":
            user = self.scope['user']
            if  user.is_authenticated and user.is_superuser:
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                await self.accept()
            else:
                self.close()
                return
        else:
            self.close()
            return

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
   
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("admin",text_data_json)

        action = text_data_json.get("action", False)
        if action == 'send.message':
            # format={
            #     'action':'send.message',
            #     'message':message,
            #     'receiver':receiver
            # }
            message = text_data_json.get("message", None)
            receiver = text_data_json.get("receiver", None)
            receiver="fc1a9fde-54a3-4c61-9c5b-aa18f31199d1"
            if message and receiver:
                await self.create_message(message,receiver)
                await self.channel_layer.group_send(
                    receiver,
                    {
                        "type": "sendto.anynomous",
                        "message": message,
                        "receiver":receiver,
                    }
                    )

        elif action == "type.message":
            # format={
            #     'action':'type.message',
            #     'receiver':receiver
            # }
            receiver = text_data_json.get("receiver", None)
            receiver="fc1a9fde-54a3-4c61-9c5b-aa18f31199d1"
            if receiver:
                await self.channel_layer.group_send(
                    receiver,
                    {
                        "type": "typeto.anynomous",
                        "receiver":receiver,
                    }
                    )

    async def create_message(self, message,receiver):
        room, found = await self.get_room(receiver)
        if not found:
            return
        await database_sync_to_async(AnonymousRoomMessage.objects.create)(
            room=room,
            message=message,
            sender_type='ADMIN',  
            sent_time=timezone.now(),
            read=False
        )

    async def get_room(self, receiver):
        try:
            room = await database_sync_to_async(AnonymousRoom.objects.get)(room_name=receiver)
            found = True
        except AnonymousRoom.DoesNotExist:
            room = None
            found = False  # Set created to False since the room wasn't created
        return room, found