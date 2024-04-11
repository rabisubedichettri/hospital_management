import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import AnonymousRoom, AnonymousRoomMessage
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

class AnonymousConsumer(AsyncWebsocketConsumer):

    async def sendto_admin(self, event):
        await self.send(text_data=json.dumps({
            "action": "typing.message",
            # "sender":self.room_group_name,
              "sender":"any sendto_admin",
            }))
    
    async def sendto_anynomous(self, event):
        # this handler is used to send message to admin called by reply_me
        data={
        "action":"got.message",
        'message':event["message"],
        # "sender":event['sender'],
          "sender":"any sendto_amy",
        }
        await self.send(text_data=json.dumps(data))

    #working
    async def typeto_admin(self,event):
        # run:anynomous status:replyback to anynomous only
        await self.send(text_data=json.dumps({
            "action": "typing.message",
            "sender":"call me",
            }))

    async def sendto_admin(self, event):
        await self.send(text_data=json.dumps({
            "action": "typing.message",
            "sender":"called me",
            }))

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
        print("admin",text_data_json)

        action = text_data_json.get("action", False)
        if action == 'send.message':
            # format={
            #     'action':'send.message',
            #     'message':message,
                 
            # }
            message = text_data_json.get("message", None)
            if message:
                await self.create_message(message)

        elif action == "type.message":
            # format={
            #     'action':'type.message',
            # }
            await self.send_typing_status(self.room_group_name)

    async def create_message(self, message):
        room, found = await self.get_room(self.room_group_name)
        if not found:
            return
        await database_sync_to_async(AnonymousRoomMessage.objects.create)(
            room=room,
            message=message,
            sender_type='ANONYMOUS',  
            sent_time=timezone.now(),
            read=False
        )

        await self.channel_layer.group_send(
            'admin',
            {
                "type": "sendto.admin",
                "message": message,
                'sender':self.room_group_name,
            }
        )

    async def send_typing_status(self,receiver):
        await self.channel_layer.group_send(
            receiver,
            {
                "type": "typeto.admin",
            }
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

    # working 
    # anynomous: send message, status: data goes to admin
    async def typeto_admin(self,event):

        await self.send(text_data=json.dumps({
            "action": "typing.message",
            "sender":"a:self.room_group_name",
            }))

    async def sendto_admin(self, event):
        await self.send(text_data=json.dumps({
            "action": "typing.message",
            "sender":"self.room_group_name",
            }))
    
    async def sendto_anynomous(self, event):
        # this handler is used to send message to admin called by reply_me
        data={
        "action":"got.message",
        'message':event["message"],
        "sender":event['sender'],
        }
        await self.send(text_data=json.dumps(data))

    async def typeto_anynomous(self,event):
        await self.send(text_data=json.dumps({
            "action": "typing.message",
            "sender":self.room_group_name,
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
            if message and receiver:
                await self.create_message(message, receiver)

        elif action == "type.message":
            # format={
            #     'action':'type.message',
            #     'receiver':receiver
            # }
            receiver = text_data_json.get("receiver", None)
            if sender:
                await self.send_typing_status(receiver)

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

        # it sends mesage to all admin who is listening to it
        await self.channel_layer.group_send(
            receiver,
            {
                "type": "sendddd.message",
                "message": message,
                "receiver":"fc1a9fde-54a3-4c61-9c5b-aa18f31199d1",
            }
        )

    # both are conneted working
 

    async def sendddd_message(self, event):
        #  admin send messae to anynomous,  status:message got by admin
        data={
        "action":"got.messagce",
        'message':event["message"],
        "client":"yes"  
        }
        await self.send(text_data=json.dumps(data))
        # this make sure all bordcast to own e

    # bordacast to all admin
    async def send_typing_status(self,receiver):
        await self.channel_layer.group_send(
            receiver,
            {
                "type": "sendto.anynomous",
            }
        )

    async def type_message(self, event):
        await self.send(text_data=json.dumps({
            "action": "typeto.anynomous"
            }))

    async def get_room(self, receiver):
            try:
                room = await database_sync_to_async(AnonymousRoom.objects.get)(room_name=receiver)
                found = True
            except AnonymousRoom.DoesNotExist:
                room = None
                found = False  # Set created to False since the room wasn't created
            return room, found
