from django.core.files import File
from datetime import datetime
from django.utils import timezone
from django.core.files.storage import FileSystemStorage, default_storage
import os
import base64
import sched
import time
from enum import Enum
from django.conf import settings
from .models import ForgeLink
from chat.models import Connected, Presence
from django.conf import settings


def is_ajax(request):  # need to move this function into function for DRY
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class connectionRequestStatus(Enum):
    NO_CON_REQUEST = 0
    YOU_SENT_CON_REQUEST = 1
    THEY_SENT_CON_REQUEST = 2


def get_forge_link_or_false(sender, receiver):
    try:
        return ForgeLink.objects.get(sender=sender, receiver=receiver, is_active=True)
    except ForgeLink.DoesNotExist:
        return False


def save_Base64_Temp_ImageString(imageString):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        url = os.path.join(settings.TEMP, "temp_image_profile.png")
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open("", "wb+") as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_Base64_Temp_ImageString(imageString)
    return None


def convertDimensions(dimension):
    return int(float(str(dimension)))


def prune_presence(con_queryset):
    MAX_AGE = settings.CHANNELS_PRESENCE_MAX_AGE

    if con_queryset:
        for con in con_queryset:
            try:
                presence = Presence.objects.get(
                    channel_name=con.channel_name, user=con.user)
                if int((timezone.now() - presence.last_seen).total_seconds()) > MAX_AGE:
                    con.delete()
                    presence.delete()
            except Presence.DoesNotExist:
                pass

    else:
        print("there are no presences")
