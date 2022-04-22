from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .decorators import allowedToChatWith
from Connection.models import ConnectionsList
from django.db.models import Q
from .models import singleOneToOneRoom
from social.models import Notification
User = get_user_model()

# need to pass also the test_func user to see if they are friends or not.


@login_required
@allowedToChatWith
def Chat(request, username, *args, **kwargs):
    current_user = request.user
    current_user_connections = ConnectionsList.objects.get(
        user=current_user).connections.all()
    other_user = get_object_or_404(User, username=username)
    msg_notifications = Notification.objects.filter(
        user_to=request.user, type_off=6)
    for notif in msg_notifications:
        notif.seen = True
        notif.save()
    lookup = Q(first_user=current_user, second_user=other_user) | Q(
        first_user=other_user, second_user=current_user)
    room = singleOneToOneRoom.objects.filter(lookup)
    msges = room.first().messages.all()
    context = {"other_user": other_user,
               "all_users": current_user_connections, "msges": msges, }
    return render(request, "landing/message.html", context)
