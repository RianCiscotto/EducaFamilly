from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .models import Message

User = get_user_model()


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        user_type = request.POST.get("user_type")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe!")
            return redirect("register")

        if user_type not in ["teacher", "parent"]:
            messages.error(request, "Selecione um tipo de usuário válido.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name,
            user_type=user_type
        )

        messages.success(request, "Conta criada! Faça login.")
        return redirect("login")

    return render(request, "chat/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("conversations")

        return render(
            request,
            "chat/login.html",
            {
                "error": "Usuário ou senha incorretos"
            }
        )

    return render(request, "chat/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def conversations(request):

    if request.user.user_type == "teacher":
        users = User.objects.exclude(
            id=request.user.id
        )

    else:
        users = User.objects.filter(
            user_type="teacher"
        )

    # Calcula a quantidade de mensagens não lidas
    # de cada usuário para o usuário logado.
    for user in users:

        user.unread_count = Message.objects.filter(
            sender=user,
            receiver=request.user,
            read=False
        ).count()

    return render(
        request,
        "chat/usuarios.html",
        {
            "users": users
        }
    )




@login_required
def chat_with(request, user_id):
    other = get_object_or_404(
        User,
        id=user_id
    )

    # Responsável só pode conversar com Professor
    if (
        request.user.user_type == "parent"
        and other.user_type != "teacher"
    ):
        return redirect("conversations")

    if request.method == "POST":
        text = request.POST.get("text")

        if text:
            Message.objects.create(
            sender=request.user,
            receiver=other,
            text=text
            )

        return redirect(
            "chat_with",
            user_id=other.id
        )

    msgs = Message.objects.filter(
    sender__in=[request.user, other],
    receiver__in=[request.user, other]
    ).order_by("timestamp")
    
    Message.objects.filter(
    sender=other,
    receiver=request.user,
    read=False
    ).update(
    read=True
    )

    return render(
        request,
        "chat/chat.html",
        {
            "other": other,
            "messages": msgs
        }
    )