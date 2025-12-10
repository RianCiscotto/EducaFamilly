from django.urls import path
from . import views
from .views import login_view

urlpatterns = [
    path("", views.conversations, name="conversations"),
    path("<int:user_id>/", views.chat_with, name="chat_with"),
    path("login/", login_view, name="login"),
    path("register/", views.register, name="register"),


]
