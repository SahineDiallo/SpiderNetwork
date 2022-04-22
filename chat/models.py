from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q, F
User = get_user_model()

# create a single room between 2 connected users


class singleOneToOneRoom(models.Model):
    first_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="first_user")
    second_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="second_user")

    room_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.first_user.useranme} and {self.second_user.username} room'


class messages(models.Model):
    room = models.ForeignKey(
        singleOneToOneRoom, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="msg_sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="msg_receiver")
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}_to_{self.receiver}'


class Connected(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="connected")
    room_name = models.CharField(max_length=100, null=False)
    channel_name = models.CharField(max_length=100, null=False)
    connect_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Presence(models.Model):
    room = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='presence')
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.room} presence'

    def updateLastSeen(self):
        self.last_seen = timezone.now()
        self.save()

    def leaveAll(self):
        self.delete()
