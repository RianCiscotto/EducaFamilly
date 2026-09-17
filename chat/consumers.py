
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Message


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    # =========================================
    # CONECTAR AO CHAT
    # =========================================

    async def connect(self):

        self.user = self.scope["user"]

        # Usuário não autenticado
        if self.user.is_anonymous:
            await self.close()
            return

        # ID do outro usuário
        self.other_user_id = (
            self.scope["url_route"]["kwargs"]["user_id"]
        )

        # Busca o outro usuário
        self.other_user = await self.get_user(
            self.other_user_id
        )

        # Usuário não existe
        if self.other_user is None:
            await self.close()
            return

        # =========================================
        # PERMISSÃO DE CONVERSA
        # =========================================

        # Responsável só pode conversar com professor
        if (
            self.user.user_type == "parent"
            and self.other_user.user_type != "teacher"
        ):
            await self.close()
            return

        # =========================================
        # CRIA A SALA DO CHAT
        # =========================================

        # Ordenamos os IDs para que os dois usuários
        # sempre entrem na mesma sala.
        #
        # Exemplo:
        #
        # usuário 7 + usuário 8
        # chat_7_8
        #
        # Mesmo que 8 abra o chat com 7,
        # também será chat_7_8.

        user_ids = sorted([
            self.user.id,
            self.other_user.id
        ])

        self.room_group_name = (
            f"chat_{user_ids[0]}_{user_ids[1]}"
        )

        # =========================================
        # ENTRA NA SALA
        # =========================================

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceita a conexão
        await self.accept()

    # =========================================
    # DESCONECTAR DO CHAT
    # =========================================

    async def disconnect(self, close_code):

        if hasattr(
            self,
            "room_group_name"
        ):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # =========================================
    # RECEBER DADOS DO NAVEGADOR
    # =========================================

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)

        except json.JSONDecodeError:
            return

        event_type = data.get("type")

        # =====================================
        # MENSAGEM
        # =====================================

        if event_type == "message":

            text = data.get(
                "text",
                ""
            ).strip()

            if not text:
                return

            # Salva no banco
            message = await self.create_message(
                text
            )

            # Envia para todos da conversa
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",

                    "message": message["text"],

                    "sender": message["sender"],

                    "sender_id": message["sender_id"],

                    "timestamp": message["timestamp"],
                }
            )

        # =====================================
        # DIGITANDO
        # =====================================

        elif event_type == "typing":

            is_typing = data.get(
                "is_typing",
                False
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",

                    "user_id": self.user.id,

                    "username": self.user.username,

                    "is_typing": is_typing,
                }
            )

    # =========================================
    # EVENTO: NOVA MENSAGEM
    # =========================================

    async def chat_message(
        self,
        event
    ):

        await self.send(
            text_data=json.dumps({

                "type": "message",

                "text": event["message"],

                "sender": event["sender"],

                "sender_id": event["sender_id"],

                "timestamp": event["timestamp"],

            })
        )

    # =========================================
    # EVENTO: USUÁRIO DIGITANDO
    # =========================================

    async def user_typing(
        self,
        event
    ):

        # Não envia o evento de volta
        # para quem está digitando.

        if (
            event["user_id"]
            == self.user.id
        ):
            return

        await self.send(
            text_data=json.dumps({

                "type": "typing",

                "user_id": event["user_id"],

                "username": event["username"],

                "is_typing": event["is_typing"],

            })
        )

    # =========================================
    # BANCO DE DADOS
    # =========================================

    @database_sync_to_async
    def get_user(
        self,
        user_id
    ):

        try:

            return User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:

            return None

    @database_sync_to_async
    def create_message(
        self,
        text
    ):

        message = Message.objects.create(

            sender=self.user,

            receiver=self.other_user,

            text=text

        )

        return {

            "text": message.text,

            "sender": message.sender.username,

            "sender_id": message.sender.id,

            "timestamp": (
                message.timestamp.isoformat()
            ),

        }

