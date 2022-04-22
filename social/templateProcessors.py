from .models import Notification


def active_notifications(request, *args, **kwargs):
    current_user = request.user
    if current_user.is_authenticated:
        notifications = Notification.objects.filter(
            user_to=current_user).exclude(type_off=6)[:10]
        notifs_count = Notification.objects.filter(
            user_to=current_user, seen=False).exclude(type_off=6).count()
        msg_notifications = Notification.objects.filter(
            user_to=current_user, type_off=6)[:10]
        msg_notifs_count = Notification.objects.filter(
            user_to=current_user, seen=False, type_off=6).count()
        return {"notifications": notifications, "notif_count": notifs_count, "msg_notifications": msg_notifications, "msg_notif_count": msg_notifs_count}
    return {}
