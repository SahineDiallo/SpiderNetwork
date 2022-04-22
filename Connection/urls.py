from django.urls import path
from .views import (
    getUserProfileForm,
    crop_image,
    Sending_Link_Forge,
    cancelForgeLink,
    acceptForgeLink,
    deleteForgeLink,
    Unlink,
    cleanUnreadNotif,
    prunePresenceAjaxView
)

urlpatterns = [
    path("update-profile/<slug:profile_slug>/",
         getUserProfileForm, name="edit-profile"),
    path("cropping-image/", crop_image, name="crop-image"),
    path("sending-link-forge/", Sending_Link_Forge, name="sending-link-forge"),
    path("cancel-forge-link/", cancelForgeLink, name="cancel-link-forge"),
    path("accept-forge-link/", acceptForgeLink, name="accept-link-forge"),
    path("delete-forge-link/", deleteForgeLink, name="delete-link-forge"),
    path("unlink-forge-link/", Unlink, name="unlink-link-forge"),
    path("cleanUnreadNotif/", cleanUnreadNotif, name="cleanUnreadNotif"),
    path("prune_presence/", prunePresenceAjaxView, name="prunePresenceAjaxView"),
]
