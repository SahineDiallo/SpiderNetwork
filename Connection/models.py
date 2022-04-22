from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ConnectionsList(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="ConnectionsList")
    connections = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.user}'s connecton list"

    def addLink(self, new_link):  # adding someone to your connection list
        if not new_link in self.connections.all():
            self.connections.add(new_link)

    def removeLink(self, old_link):  # removing someone to yuur connection list
        if old_link in self.connections.all():
            self.connections.remove(old_link)

    def unlink(self, removee):  # Breaking a connection between you and someone else
        linkBreaker = self  # user who is terminated the connection
        linkBreaker.removeLink(removee)
        # and let's remove the linkBreaker to the list of the removee
        # which is the user he removed from his list of connections
        removee_ConnectionsList = ConnectionsList.objects.get(user=removee)
        removee_ConnectionsList.removeLink(self.user)

    def areLinked(self, link):
        return True if link in self.connections.all() else False


class ForgeLink(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(default=True, )
    date_sent = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender}'s request for link"

    # override the save method and see if there is any cancelled request
    # in case the user wants to forge a link and sends the request again

    def accept(self):  # agree to forge a link with the sender
        sender_links_list = ConnectionsList.objects.get(user=self.sender)
        receiver_links_list = ConnectionsList.objects.get(user=self.receiver)
        if sender_links_list:  # which should exist since we create one for any new user
            sender_links_list.addLink(self.receiver)
            if receiver_links_list:  # Again should exists
                receiver_links_list.addLink(self.sender)
                self.is_active = False  # now this link request is solved

    def decline(self):  # Not accepting to forge a link with the sender
        self.is_active = False

    def Cancel(self):  # Cancelling the the link you wanned to forge with someone else
        self.is_active = False
        # and let's delete it from the database
