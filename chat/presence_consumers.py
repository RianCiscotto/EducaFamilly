import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .presence import ONLINE_USERS


class PresenceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # Não autenticado
        if self.user.is_anonymous:
            await self.close()
            return

        self.presence_group = "global_presence"

        # Entra na sala global de presença
        await self.channel_layer.group_add(
            self.presence_group,
            self.channel_name
        )

        await self.accept()

        # -----------------------------------------
        # USUÁRIO ENTROU ONLINE
        # -----------------------------------------

        was_offline = self.user.id not in ONLINE_USERS

        ONLINE_USERS[self.user.id] = (
            ONLINE_USERS.get(self.user.id, 0) + 1
        )

        # Envia para o próprio usuário
        # a situação atual dos outros usuários
        online_users = list(ONLINE_USERS.keys())

        last_seen_users = await self.get_last_seen_users()

        await self.send(
            text_data=json.dumps({
                "type": "initial_presence",
                "online_users": online_users,
                "last_seen": last_seen_users,
            })
        )

        # Se realmente estava offline antes,
        # avisa os demais
        if was_offline:
            await self.channel_layer.group_send(
                self.presence_group,
                {
                    "type": "presence_update",
                    "user_id": self.user.id,
                    "online": True,
                    "last_seen": None,
                }
            )

    async def disconnect(self, close_code):
        if not hasattr(self, "user"):
            return

        await self.channel_layer.group_discard(
            self.presence_group,
            self.channel_name
        )

        # -----------------------------------------
        # REMOVE UMA CONEXÃO
        # -----------------------------------------

        if self.user.id not in ONLINE_USERS:
            return

        ONLINE_USERS[self.user.id] -= 1

        # Só fica offline quando a ÚLTIMA
        # conexão for encerrada
        if ONLINE_USERS[self.user.id] <= 0:
            del ONLINE_USERS[self.user.id]

            # Salva o último acesso
            await self.update_last_seen()

            # Hora em que ficou offline
            last_seen = timezone.now().isoformat()

            # Avisa todos
            await self.channel_layer.group_send(
                self.presence_group,
                {
                    "type": "presence_update",
                    "user_id": self.user.id,
                    "online": False,
                    "last_seen": last_seen,
                }
            )

    async def presence_update(self, event):
        # Não precisa mandar a própria mudança
        # para o próprio usuário
        if event["user_id"] == self.user.id:
            return

        await self.send(
            text_data=json.dumps({
                "type": "presence",
                "user_id": event["user_id"],
                "online": event["online"],
                "last_seen": event["last_seen"],
            })
        )

    @database_sync_to_async
    def get_last_seen_users(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        users = User.objects.exclude(
            id=self.user.id
        ).values(
            "id",
            "last_seen"
        )

        result = {}

        for user in users:
            result[str(user["id"])] = (
                user["last_seen"].isoformat()
                if user["last_seen"]
                else None
            )

        return result

    @database_sync_to_async
    def update_last_seen(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        User.objects.filter(
            id=self.user.id
        ).update(
            last_seen=timezone.now()
        )


