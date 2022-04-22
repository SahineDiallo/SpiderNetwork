from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import edit
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse
from .models import Post, Files, UserProfile, Comment, UserFollowing, Notification
from django.template.loader import render_to_string
from .forms import PostForm, CommentPostForm, UserProfileForm
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import requires_csrf_token
from django.core.files.storage import FileSystemStorage
from Connection.models import ForgeLink, ConnectionsList
from django.core import serializers
import json
from django.template.loader import render_to_string
from django.db.models import Q
from Connection.utils import get_forge_link_or_false, connectionRequestStatus
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
User = get_user_model()


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = PostForm()
        commentForm = CommentPostForm()
        posts = Post.objects.all().order_by("-date_posted")
        followers = request.user.followers.count()
        following = request.user.following.count()
        context = {"posts": posts, "form": form, "commentForm": commentForm,
                   'followers': followers, 'following': following, }
        return render(request, 'social/post-list.html', context)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None, request.FILES or None)
        result = {}
        files = request.FILES.getlist('images')
        if is_ajax(request=request) and form.is_valid():
            post_obj = form.save(commit=False)
            post_obj.author = request.user
            post_obj.save()
            for file in files:
                new_img = Files(image=file)
                new_img.save()
                post_obj.images.add(new_img)
            post_obj.save()
            context = {"post": post_obj, }
            template = render_to_string(
                "social/new_post.html", context, request=request)
            result['success'] = True
            result['template'] = template
            return JsonResponse(result)
        else:
            result['success'] = False
            csrf_cxt = {}
            csrf_cxt.update(csrf(request))
            formErrors = render_crispy_form(form, context=csrf_cxt)
            result['formErrors'] = formErrors
            return JsonResponse(result)
        context = {"form": form, }

        return render(request, 'social/post-create.html', context)


class PostDeleteView(View):
    def post(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, post_slug=post_slug)
        if is_ajax(request=request):
            post.delete()
            return JsonResponse({"success": True})


class UpdatePostView(LoginRequiredMixin, View):
    def get(self, request, post_slug, *args, **kwargs):
        if is_ajax(request=request):
            post = Post.objects.get(post_slug=post_slug)
            form = PostForm(instance=post)
            context = {"form": form, "post": post, }
            template = render_to_string(
                "social/getEditForm.html", context, request=request)
            return JsonResponse({"template": template, })

    def post(self, request, post_slug, *args, **kwargs):
        post = Post.objects.get(post_slug=post_slug)
        form = PostForm(request.POST or None,
                        request.FILES or None, instance=post)
        result = {}
        files = request.FILES.getlist("images")
        if is_ajax(request=request) and form.is_valid():

            post_obj = form.save()
            Files.objects.filter(post=post).delete()
            post.images.clear()  # clearing all the old instances
            for img in files:
                img = Files(image=img)
                img.save()
                post.images.add(img)
            post_obj.save()
            context = {"post": post_obj, }
            template = render_to_string(
                "social/new_post.html", context, request=request)
            result["post_slug"] = post_obj.post_slug
            result["template"] = template
            result["success"] = True
            return JsonResponse(result)
        else:
            result['success'] = False
            csrf_cxt = {}
            csrf_cxt.update(csrf(request))
            formErrors = render_crispy_form(form, context=csrf_cxt)
            result['formErrors'] = formErrors
            return JsonResponse(result)


class DetailPostView(View):
    def get(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, post_slug=post_slug)
        context = {"post": post, }
        return render(request, "social/post-detail.html", context)

    def post(self, request, post_slug, *args, **kwargs):
        pass
        # the post will be about the comment on this post or images
        # of the post itself


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_slug, *args, **kwargs):
        noPadding = True  # this will help remove the padding in the profile page
        form = UserProfileForm()
        profile = get_object_or_404(UserProfile, profile_slug=user_slug)
        current_user = request.user
        posts = Post.objects.filter(author__profile__profile_slug=user_slug)
        # We have different states depending on who is looking to the profile and the
        # relationship that they do have with the owner of the profile
        ForgeLinkStatus = None  # by default
        follower = False
        followers = profile.user.followers.count()
        following = profile.user.following.count()
        request_sender = None
        forgeLink_id = None
        connections = None
        con_request = ForgeLink.objects.filter(
            receiver=profile.user, is_active=True)
        is_profile_owner = True  # by default
        are_connected = False  # by default
        if profile.user == current_user:
            # CASE 1 user looking to his own profile
            is_profile_owner = True
            con_list = ConnectionsList.objects.get(user=profile.user)
            connections = con_list.connections.all()
        else:  # that means the user is looking to another user's profile
            is_profile_owner = False
            for flw in profile.user.followers.all():
                if flw.user_id.id == current_user.id:
                    follower = True
            # getting all the connectins of the current profile
            con_list = ConnectionsList.objects.get(user=profile.user)
            connections = con_list.connections.all()
            if current_user in connections:  # CASE 2
                are_connected = True  # means they are connected
            else:
                are_connected = False  # they are not connected at all
                if get_forge_link_or_false(sender=profile.user, receiver=current_user) != False:
                    # means they sent you a forge link CASE 3
                    ForgeLinkStatus = connectionRequestStatus.THEY_SENT_CON_REQUEST.value
                    forgeLink_id = get_forge_link_or_false(
                        sender=profile.user, receiver=current_user).id
                    request_sender = profile.user.username
                elif get_forge_link_or_false(sender=current_user, receiver=profile.user) != False:
                    # means you sent them a forge link CASE 4
                    ForgeLinkStatus = connectionRequestStatus.YOU_SENT_CON_REQUEST.value
                    forgeLink_id = get_forge_link_or_false(
                        sender=current_user, receiver=profile.user).id
                else:  # means none of you sent the other a forget link CASE 5
                    ForgeLinkStatus = connectionRequestStatus.NO_CON_REQUEST.value
        context = {
            "profile": profile, "posts": posts,
            "form": form, "no_padding": noPadding,
            "is_profile_owner": is_profile_owner,
            "forgeLink_id": forgeLink_id,
            "connections": connections,
            "con_request": con_request,
            "ForgeLinkStatus": ForgeLinkStatus,
            "req_sender": request_sender,
            "follower": follower,
            "followers": followers,
            "following": following,
        }
        return render(request, "landing/profile.html", context)


def JobsView(request):
    return render(request, 'landing/jobs.html')


class CreateCommentPostView(View):
    def post(self, request, post_slug, *args, **kwargs):
        current_user = request.user
        post = get_object_or_404(Post, post_slug=post_slug)
        form = CommentPostForm(request.POST or None)
        if is_ajax(request=request) and form.is_valid():
            comment_post = form.save(commit=False)
            comment_post.author = request.user
            comment_post.post = post
            comment_post.save()
            # let's notfify the author of the post about the comment
            channel_layer = get_channel_layer()
            room_name = f"comment_or_post_listener_{post.author.id}"
            new_notif = Notification.objects.create(
                user_from=current_user,
                user_to=post.author,
                message="has commented on one of your posts",
                type_off=3
            )
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    "type": "send_notification_to_post_author",
                    "liker": current_user.username,
                    "notification": "has liked your post",
                    "avatar_url": current_user.profile.avatar.url,
                    "date_notif": new_notif.date_sent,
                    "notif_type": new_notif.type_off,
                }
            )
            jsonInstance = serializers.serialize(
                "json",
                [
                    comment_post,
                ],
                use_natural_foreign_keys=True,  # I don't use one for now
            )
            result = {}
            result["success"] = True
            result["comment_obj"] = jsonInstance
            result["imageUrl"] = comment_post.author.profile.avatar.url
            result["comment_pk"] = comment_post.pk
            return JsonResponse(result)
        result = {"success": False}
        return JsonResponse(result)


class DeleteCommentPostView(View):
    def post(self, request, comment_id, *args, **kwargs):
        if is_ajax(request=request):
            comment = get_object_or_404(Comment, id=comment_id)
            post_slug = comment.post.post_slug
            comment.delete()
        return JsonResponse({"success": True, "post_slug": post_slug, })


class AddRemovePostLikes(LoginRequiredMixin, View):
    def post(self, request, post_or_comment_slug, *args, **kwargs):
        current_user = request.user
        if is_ajax(request=request):
            liked_a = request.POST.get("liked_a")
            is_liked = None
            channel_layer = get_channel_layer()
            if liked_a == "comment":
                comment = get_object_or_404(
                    Comment, comment_slug=post_or_comment_slug)
                is_liked = comment.likes.filter(
                    username=request.user.username).exists()
                if not is_liked:
                    comment.likes.add(request.user)
                    comment.save()  # do not think this step is necessary though

                else:
                    comment.likes.remove(request.user)
                    comment.save()
            else:
                post = get_object_or_404(Post, post_slug=post_or_comment_slug)
                is_liked = post.likes.filter(
                    username=request.user.username).exists()
                if not is_liked:
                    post.likes.add(request.user)
                    post.save()
                    # now let's handle the notification of comment author
                    new_notif = Notification.objects.create(
                        user_from=current_user,
                        user_to=post.author,
                        message="has liked one of your posts",
                        type_off=2
                    )
                    room_name = f"comment_or_post_listener_{post.author.id}"
                    async_to_sync(channel_layer.group_send)(
                        room_name,
                        {
                            "type": "send_notification_to_post_author",
                            "liker": current_user.username,
                            "notification": "has liked your post",
                            "avatar_url": current_user.profile.avatar.url,
                            "date_notif": new_notif.date_sent,
                            "notif_type": new_notif.type_off,
                        }
                    )
                else:
                    post.likes.remove(request.user)
                    post.save()
            return JsonResponse({"is_liked": is_liked})


class AddRemoveFollowers(LoginRequiredMixin, View):
    def post(self, request, profile_slug, *args, **kwargs):
        payload = dict()
        user = request.user
        data_name = request.POST.get("data_name")
        try:
            profile = UserProfile.objects.get(profile_slug=profile_slug)
            payload["following"] = profile.user.username
            if data_name == "flww":
                try:
                    user_fol = UserFollowing.objects.get(
                        user_id=user, following_user_id=profile.user)
                    if user_fol:
                        payload['error'] = "You are already following this profile"
                except UserFollowing.DoesNotExist:
                    UserFollowing.objects.create(
                        user_id=user, following_user_id=profile.user)
                    payload['success'] = True
            elif data_name == "unflww":
                try:
                    user_fol = UserFollowing.objects.get(
                        user_id=user, following_user_id=profile.user)
                    user_fol.delete()
                    payload["success"] = True
                except UserFollowing.DoesNotExist:
                    payload['error'] = "You are not following this profile"
        except UserProfile.DoesNotExist:
            payload['error'] = "Sorry, But following or unfollowing this profile now is not possible. Try later..."
        return JsonResponse(payload)


class ConnectionsListView(LoginRequiredMixin, View):
    def get(self, request, profile_slug, *arg, **kwargs):
        user = UserProfile.objects.get(profile_slug=profile_slug).user
        is_profile_owner = user == self.request.user
        con_list = ConnectionsList.objects.get(user=user)
        connections = con_list.connections.all()  # get all the conn of the user
        con_request = ForgeLink.objects.filter(receiver=user, is_active=True)
        context = {
            "connections": connections,
            "con_request": con_request,
            "is_profile_owner": is_profile_owner,
        }
        return render(request, "connection/connectionslist.html", context)

        # do not think I will need to write a test func for this view


class searchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        req_sender = None
        user_links = ConnectionsList.objects.get(user=user)
        q = request.GET.get("q")
        ForgeLinkStatus = None
        forgeLink_id = None

        found_users = User.objects.filter(
            Q(username__icontains=q) | Q(
                email__icontains=q) | Q(profile__full_name__icontains=q)
        ).distinct()
        search_list_result = []
        for a_user in found_users:
            if not user_links.areLinked(a_user):
                are_connected = False  # they are not connected at all
                if get_forge_link_or_false(sender=a_user, receiver=user) != False:
                    # means they sent you a forge link
                    req_sender = a_user
                    ForgeLinkStatus = connectionRequestStatus.THEY_SENT_CON_REQUEST.value
                    forgeLink_id = get_forge_link_or_false(
                        sender=a_user, receiver=user).id
                    request_sender = a_user.username
                elif get_forge_link_or_false(sender=user, receiver=a_user) != False:
                    # means you sent them a forge link
                    ForgeLinkStatus = connectionRequestStatus.YOU_SENT_CON_REQUEST.value
                    forgeLink_id = get_forge_link_or_false(
                        sender=user, receiver=a_user).id
                else:  # means none of you sent the other a forget link
                    ForgeLinkStatus = connectionRequestStatus.NO_CON_REQUEST.value
            search_list_result.append(
                (a_user, user_links.areLinked(a_user), ForgeLinkStatus, forgeLink_id))
        context = {
            "found_users_list": search_list_result,
            "req_sender": req_sender,
        }
        return render(request, "social/search_result.html", context)
