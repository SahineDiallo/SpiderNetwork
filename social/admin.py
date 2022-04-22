from django.contrib import admin
from .models import Post, Files, UserProfile, Comment, UserFollowing, Notification


admin.site.register(Post)
admin.site.register(Files)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(UserFollowing)
admin.site.register(Notification)
