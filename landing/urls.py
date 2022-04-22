from django.urls import path
from landing import views as land_views

urlpatterns = [
    path("", land_views.IndexView.as_view(), name="index"),
]
