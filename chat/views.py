from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Message
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name
        )

        messages.success(request, "Conta criada! Faça login.")
        return redirect("login")

    return render(request, "chat/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/chat/")  # vai para lista de usuários

        return render(request, "chat/login.html", {"error": "Usuário ou senha incorretos"})

    return render(request, "chat/login.html")

User = get_user_model()

@login_required
def conversations(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat/usuarios.html", {"users": users})

@login_required
def chat_with(request, user_id):
    other = User.objects.get(id=user_id)

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Message.objects.create(
                sender=request.user,
                receiver=other,
                text=text
            )
        return redirect("chat_with", user_id=other.id)

    msgs = Message.objects.filter(
        sender__in=[request.user, other],
        receiver__in=[request.user, other]
    ).order_by("timestamp")

    return render(request, "chat/chat.html", {
        "other": other,
        "messages": msgs
    })
