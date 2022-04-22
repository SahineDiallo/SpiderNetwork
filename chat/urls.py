from django.urls import path
from .views import Chat
urlpatterns = [
    path("personalChat/<str:username>/", Chat, name="chat"),
]
