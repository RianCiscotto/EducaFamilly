from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("conversas/", views.conversations, name="conversations"),
    path("<int:user_id>/", views.chat_with, name="chat_with"),
]