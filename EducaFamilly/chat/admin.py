from django.contrib import admin
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "text", "timestamp")
    list_filter = ("sender", "receiver")
