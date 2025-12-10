from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.urls import path
def redirect_to_login(request):
    return redirect("login")  # nome da URL de login dentro do chat

urlpatterns = [
    path("", redirect_to_login, name="root"),  # 👈 redireciona / para login
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
