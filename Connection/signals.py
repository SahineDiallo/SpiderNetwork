from django.db.models.signals import post_save, pre_delete
from chat.models import Connected, Presence
from django.dispatch import receiver


@receiver(post_save, sender=Connected)
def create_presence(sender, instance, created, *args, **kwargs):
    if created:
        Presence.objects.create(
            room=instance.room_name, channel_name=instance.channel_name, user=instance.user)


@receiver(pre_delete, sender=Connected)
def updateLastSeen(sender, instance, **kwargs):
    # get the presence associated with the connected channel name
    try:
        presence = Presence.objects.get(channel_name=instance.channel_name)
        presence.updateLastSeen()
    except Presence.DoesNotExist:
        pass
