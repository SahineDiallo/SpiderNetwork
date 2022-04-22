from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify


class Files(models.Model):
    image = models.ImageField(upload_to="post/images")


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField(Files)
    content = models.TextField()
    post_slug = models.SlugField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User,  related_name="likes", blank=True,)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author}'s post"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    image = models.ForeignKey(
        Files, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    comment_slug = models.SlugField(blank=True, null=True)
    likes = models.ManyToManyField(
        User,  related_name="comment_likes", blank=True,)
    date_commented = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author}'s comment"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        default="default/default.png", upload_to="users/avatar/")
    full_name = models.CharField(max_length=200, blank=True, null=True)
    work_at = models.CharField(
        default="No work at or school", max_length=200, blank=True, null=True)
    bio = models.TextField(default="no bio provided", blank=True, null=True)
    location = models.CharField(
        default="no location provided", max_length=200, blank=True, null=True)
    profile_slug = models.SlugField()
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class UserFollowing(models.Model):
    user_id = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'following_user_id'],  name="unique_followers")
        ]

        ordering = ["-created"]

    def __str__(self):
        return f"{self.user_id.username} follows {self.following_user_id.username}"


class Notification(models.Model):
    type_of = (
        ("1", "new_post"),
        ("2", "liked_post"),
        ("3", "commented_post"),
        ("4", "acceted_connection"),
        ("5", "sent_connection"),
    )
    user_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notif_from", blank=True, null=True)
    user_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notif_to", blank=True, null=True)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    type_off = models.CharField(max_length=200, choices=type_of, default="1")
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"notif_from_{self.user_from.username}"

    class Meta:
        ordering = ("-date_sent",)
