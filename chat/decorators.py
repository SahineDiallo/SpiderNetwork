from Connection.models import ConnectionsList
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.messages import constants as messsages
User = get_user_model()

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}


def allowedToChatWith(func_view):
    def wrapper_func(request, username, *args, **kwargs):
        other_user = get_object_or_404(User, username=username)
        user = request.user
        user_con = ConnectionsList.objects.get(user=user)
        if not user_con.areLinked(other_user):
            messages.error(
                request, "Sorry! but you can only chat with people that you are connected with.")
            raise PermissionDenied  # might change this to the post list view.
        else:
            return func_view(request, username, *args, **kwargs)
    return wrapper_func
