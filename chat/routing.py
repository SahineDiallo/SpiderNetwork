from django.urls import re_path
from .consumers import PersonalChatConsumer, NotifyFollowersConsumer, LikedOrCommentedOnPostConsumer

websocket_urlpatterns = [
    re_path(r'ws/personalChat/(?P<id>\d+)/$',
            PersonalChatConsumer.as_asgi()),
    re_path(r'ws/user-followers-notification/$',
            NotifyFollowersConsumer.as_asgi()),
    re_path(r'ws/post-likeOrComment-notification/$',
            LikedOrCommentedOnPostConsumer.as_asgi()),
]
