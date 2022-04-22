from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import singleOneToOneRoom, messages, Connected, Presence
from social.models import Notification
from channels.db import database_sync_to_async
from django.db.models import Q
from django.contrib.auth import get_user_model
import json
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async

User = get_user_model()


@sync_to_async
def connect_user(room_name, user, channel_name):
    if user:
        Connected.objects.create(
            user=user, room_name=room_name, channel_name=channel_name)
    else:
        pass
    return None


@sync_to_async
def disconnect_user(room_name, user, channel_name):
    if user:
        try:
            get_object_or_404(Connected, Q(user=user), Q(
                room_name=room_name), Q(channel_name=channel_name))
        except:
            pass
        else:
            user = get_object_or_404(Connected, Q(user=user), Q(
                room_name=room_name), Q(channel_name=channel_name))
            user.delete()
            print("the user has been deleted from the connected model")
    return None


class NotifyFollowersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        current_user = self.scope['user']
        # check if the user is authenticated
        if current_user.is_anonymous:
            self.close()
        self.group_room_name = f'follower_user_{current_user.id}'
        await self.channel_layer.group_add(self.group_room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        current_user = self.scope['user']
        # REMOVE the followers from room
        await self.channel_layer.group_discard(self.group_room_name, self.channel_name)

    # event will contain the msg and username
    async def send_notification_to_followers(self, event):
        '''
        Call back function to send message to the browser
        '''
        author_notif = event['notification_author']
        notification_msg = event['notification']
        avatar_url = event['avatar_url']
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {"message": notification_msg, "author": author_notif, "avatar_url": avatar_url, })
        )


class LikedOrCommentedOnPostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        current_user = self.scope["user"]
        if current_user.is_anonymous:
            self.close()
        self.room_name = f"comment_or_post_listener_{current_user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        current_user = self.scope['user']
        if current_user.is_anonymous:
            self.close()
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def send_notification_to_post_author(self, event):
        print("the send notification to post author function has been called")
        # get the data sent by the like or dislike view in the social.viewss
        message = event["notification"]
        liker = event["liker"]
        avatar_url = event["avatar_url"]
        notif_type = event["notif_type"]
        date_sent = event["date_notif"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {"message": message, "author": liker, "avatar_url": avatar_url, "notif_type": notif_type, })
        )


class PersonalChatConsumer(LikedOrCommentedOnPostConsumer, AsyncWebsocketConsumer):
    async def connect(self):
        current_user_id = self.scope['user'].id
        self.other_user_id = self.scope['url_route']['kwargs']['id']
        self.user1 = await self.get_user(current_user_id)
        self.user2 = await self.get_user(self.other_user_id)
        room_name = await self.get_room_name(self.user1, self.user2)
        self.room_name = room_name
        self.room_group_name = f"Chat-{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
        # add user to Connected model
        await connect_user(room_name=self.room_group_name, user=self.scope['user'], channel_name=self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data == '"heartbeat"':
            await self.updatelastSeen(self.channel_name)
        else:
            data = json.loads(text_data)
            message = data['message']
            username = data['username']
            receiver = ""
            msg_room_name = ""
            room = await self.get_room_instance(self.room_name)
            avatar_url, receiver_username = await self.create_msg_n_return_avatar_url(room, self.user1, self.user2, message)
            only_one_user = await self.only_one_connected_user(room_name=self.room_group_name, user=self.user1, channel_name=self.channel_name)
            if only_one_user:
                receiver = receiver_username
                new_notif, msg_room_name = await self.new_notification(self.user1, self.user2, self.other_user_id)

                await self.channel_layer.group_send(
                    msg_room_name,
                    {
                        'type': 'send_notification_to_post_author',
                        'notification': new_notif.message,
                        'avatar_url': avatar_url,
                        'date_notif': new_notif.date_sent,
                        'liker': new_notif.user_from.username,
                        'notif_type': new_notif.type_off,
                    }
                )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'avatar_url': avatar_url,
                    'receiver_username': receiver_username,
                }
            )

    async def chat_message(self, event):  # event will contain the msg and username
        message = event['message']
        username = event['username']
        avatar_url = event['avatar_url']
        receiver_username = event["receiver_username"]
        data_to_send = {
            "message": message,
            "username": username, "avatar_url": avatar_url,
            "receiver_username": receiver_username,
        }
        await self.send(
            text_data=json.dumps(data_to_send)
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        # Remove user from Connetced Model
        await disconnect_user(room_name=self.room_group_name, user=self.scope['user'], channel_name=self.channel_name)

    @database_sync_to_async
    def get_room_name(self, user1, user2):
        lookup = Q(first_user=user1, second_user=user2) | Q(
            first_user=user2, second_user=user1)
        room = singleOneToOneRoom.objects.filter(lookup)
        if room.exists():
            return room.first().room_name

    @database_sync_to_async
    def new_notification(self, user_from, user_to, receiver_id):
        room_name = f"comment_or_post_listener_{receiver_id}"
        new_notif = Notification.objects.create(
            user_from=user_from, user_to=user_to,
            message="sent you a new message",
            type_off=6
        )
        return (new_notif, room_name)

    @database_sync_to_async
    def updatelastSeen(self, channel_name):
        try:
            presence = Presence.objects.get(channel_name=channel_name)
            presence.updateLastSeen()
        except Presence.DoesNotExist:
            pass

    @database_sync_to_async
    def only_one_connected_user(self, room_name, user, channel_name):
        connected_users = Connected.objects.filter(
            room_name=room_name).values("user__username")
        if not connected_users:
            Connected.objects.create(
                user=user, room_name=room_name, channel_name=channel_name)
            return only_one_connected_user(self, room_name, user, channel_name)
        return connected_users and all(user == connected_users[0] for user in connected_users)

    @database_sync_to_async
    def get_user(self, _id):
        return User.objects.get(id=_id)

    @database_sync_to_async
    def get_room_instance(self, room_name):
        return singleOneToOneRoom.objects.get(room_name=room_name)

    @database_sync_to_async
    def create_msg_n_return_avatar_url(self, room, sender, receiver, message):
        msg = messages.objects.create(
            room=room, sender=sender, receiver=receiver, message_body=message)
        return (msg.sender.profile.avatar.url, receiver.username)
