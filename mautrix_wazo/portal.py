from __future__ import annotations

from typing import Any

from aiohttp import ClientSession
from mautrix.appservice import IntentAPI
from mautrix.bridge import BasePortal, BasePuppet
from mautrix.types import MessageEventContent, EventID, TextMessageEventContent, MessageType, EventType, UserID

from .config import Config
from .db.portal import Portal as DBPortal
from .puppet import Puppet
from .types import WazoMessage, WazoUUID
from .user import User


class PortalFailure(Exception):
    pass


class Portal(DBPortal, BasePortal):
    by_mxid = {}
    by_wzid = {}
    config: Config

    @classmethod
    def init_cls(cls, bridge):
        cls.config = bridge.config
        cls.matrix = bridge.matrix
        cls.az = bridge.az
        cls.loop = bridge.loop
        cls.bridge = bridge
        cls.private_chat_portal_meta = cls.config["bridge.private_chat_portal_meta"]

    def __int__(self, wazo_uuid: WazoUUID, mxid=None):
        DBPortal.__init__(self, wazo_uuid=wazo_uuid, mxid=mxid)
        BasePortal.__init__(self)

    async def save(self) -> None:
        await self.update()

    @property
    def main_intent(self) -> IntentAPI:
        if not self._main_intent:
            raise ValueError("Portal must be postinit() ed before main_intent can be used")
        return self._main_intent

    async def get_dm_puppet(self) -> BasePuppet | None:
        return None

    async def handle_matrix_message(self, sender: User, message: MessageEventContent, event_id: EventID) -> None:
        try:
            await self._handle_matrix_message(sender, message, event_id)
        except Exception as e:
            self.log.exception(f"Failed to handle Matrix event {event_id}: {e}")

    async def _handle_matrix_message(self, sender, message, event_id):
        if message.get_edit():
            raise NotImplementedError("Edits are not supported by the Wazo bridge.")
        if message.msgtype == MessageType.TEXT or message.msgtype == MessageType.NOTICE:
            base_url = self.bridge.config['wazo.api_url']
            headers = {'X-Auth-Token': self.bridge.config['wazo.api_token']}
            async with ClientSession() as session:
                url = f'{base_url}/chatd/1.0/users/{sender.wazo_uuid}/rooms/{self.wazo_uuid}/messages'
                await session.post(url, headers=headers, json={'alias': '', 'content': message.body})
        else:
            self.log.exception(f"Failed to handle Matrix event {event_id}")
            raise NotImplementedError('No time')

    @property
    def bridge_info_state_key(self) -> str:
        return f'wazo_{self.mxid}'

    @property
    def bridge_info(self) -> dict[str, Any]:
        return {
            "bridgebot": self.az.bot_mxid,
            "creator": self.main_intent.mxid,
            "protocol": {
                "id": "wazo",
                "displayname": "Wazo",
                "avatar_url": self.config["appservice.bot_avatar"],
            },
            "channel": {
                "id": str(self.wazo_uuid),
                "displayname": self.name,
                "avatar_url": self.config["appservice.bot_avatar"],
            },
        }

    async def _postinit(self):
        if self.mxid:
            self.by_mxid[self.mxid] = self
        self._main_intent = self.az.intent

    @classmethod
    async def get_by_wazo_id(cls, room_id: WazoUUID, create=True):
        """
        get instance associated with wazo room id,
        or create it
        :param room_id:
        :param create:
        :return:
        """
        if room_id in cls.by_wzid:
            return cls.by_wzid[room_id]
        # try and get from database
        portal = await super(Portal, cls).get_by_wazo_id(room_id)
        if portal:
            return portal
        if create:
            portal = cls(wazo_uuid=room_id)
            await portal._postinit()
            await portal.insert()
            cls.by_wzid[room_id] = portal
            return portal
        else:
            raise Exception

    async def handle_wazo_message(self, puppet: Puppet, message: WazoMessage):
        self.log.info("handling message(%s) from wazo user(%s) in wazo room(%s)",
                      message.event_id, puppet.wazo_uuid, message.room_id)
        assert self.mxid, "cannot handle message before matrix room has been associated to portal"

        content = TextMessageEventContent(
            msgtype=MessageType.TEXT,
            body=message.content
        )
        event_id = await self._send_message(
            puppet.intent, content=content,
            event_type=EventType.ROOM_MESSAGE
        )
        self.log.info("message dispatched to matrix (event_id=%s)", event_id)
        return event_id

    async def create_matrix_room(self, source: Puppet, participants: list[UserID]=None):
        assert self.wazo_uuid

        intent = source.intent
        # actually create a new matrix room
        room_id = await intent.create_room()

        self.mxid = room_id

        self.by_mxid[room_id] = self
        if participants:
            for uid in participants:
                await intent.invite_user(room_id, uid)
        return room_id
