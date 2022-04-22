from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.core.exceptions import ValidationError
from .models import Post, UserProfile, Comment, Notification
from django.contrib.auth.models import User
import string
import random
import os
from Connection.models import ConnectionsList

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync  # this will help to send the message


def uniqueSlugDigit(instance, size=12, new_slug=None):
    Klass = instance.__class__
    if new_slug is not None:
        slug = new_slug
    else:
        slug = "".join([random.choice(string.ascii_lowercase +
                       string.ascii_uppercase + string.digits) for n in range(size)])
    if Klass.objects.filter(post_slug=slug).exists():
        slug = "".join([random.choice(string.ascii_lowercase +
                       string.ascii_uppercase + string.digits) for n in range(size)])
        return uniqueSlugDigit(instance, size=12, new_slug=slug)
    return slug


@receiver(post_save, sender=Post)
def send_notification_to_followers(sender, instance, created, *args, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        # create a notification
        message = f"has published a new post"
        # notif = Notification.objects.create(
        #     user_from=instance.author, message=message)
        followers_list_rooms = [
            f"follower_user_{follower.user_id.id}" for follower in instance.author.followers.all()]
        for follower_room in followers_list_rooms:
            async_to_sync(channel_layer.group_send)(
                follower_room,
                {
                    "type": "send_notification_to_followers",
                    "notification_author": "CoreyMs",
                    "notification": "has published a new post",
                    "avatar_url": request.user.profile.avatar.url,
                }
            )


@receiver(m2m_changed, sender=Post.images.through)
def images_changed(sender, *args, **kwargs):
    instance = kwargs.get("instance")
    if instance.images.all().count() > 5:
        raise ValidationError("You cannot upload more than 5 images")


@receiver(pre_save, sender=Post)
def post_unique_slug(sender, instance, *args, **kwargs):
    if not instance.post_slug:
        instance.post_slug = uniqueSlugDigit(instance)


@receiver(post_save, sender=Comment)
def comment_unique_slug(sender, instance, created, *args, **kwargs):
    if created:
        instance.comment_slug = "".join([random.choice(string.ascii_lowercase +
                                        string.ascii_uppercase + string.digits) for n in range(10)]) + str(instance.id)
        instance.save()


@receiver(post_save, sender=User)
def post_unique_slug(sender, instance, created, *args, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.profile_slug = "".join([random.choice(string.ascii_lowercase +
                                                      string.ascii_uppercase + string.digits) for n in range(10)]) + str(instance.id)
        profile.save()
        # create a ConnectionsList for the new user
        userConnectionsList = ConnectionsList.objects.create(user=instance)
        userConnectionsList.save()  # do not think it is necessary though...


@receiver(pre_save, sender=UserProfile)
def delete_old_file(sender, instance, **kwargs):
    # on creation, signal callback won't be triggered
    if instance._state.adding and not instance.pk:
        return False

    try:
        # I need to check if the avatar is not the default at all
        # before deleting the image
        old_file = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return False

    # comparing the new file to the old one
    file = instance.avatar
    if not old_file == file and old_file.url != "/media/default/default.png":
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
