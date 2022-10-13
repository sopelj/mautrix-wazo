from __future__ import annotations

from typing import Any, List

from mautrix import bridge as br
from mautrix.appservice import IntentAPI
from mautrix.bridge import BasePortal, BasePuppet
from mautrix.types import MessageEventContent, EventID, TextMessageEventContent, MessageType, EventType

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

    def __int__(self, wazo_uuid: WazoUUID, mxid = None):
        DBPortal.__init__(self, wazo_uuid=wazo_uuid, mxid=mxid)
        BasePortal.__init__(self)

    async def save(self) -> None:
        await self.update()

    @property
    def main_intent(self) -> IntentAPI:
        if not self._main_intent:
            raise ValueError("Portal must be postinit()ed before main_intent can be used")
        return self._main_intent

    async def get_dm_puppet(self) -> BasePuppet | None:
        pass

    async def handle_matrix_message(self, sender: br.BaseUser, message: MessageEventContent, event_id: EventID) -> None:
        pass

    @property
    def bridge_info_state_key(self) -> str:
        pass

    @property
    def bridge_info(self) -> dict[str, Any]:
        pass

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
        elif create:
            portal = cls(wazo_uuid=room_id)
            await portal._postinit()
            # save in database
            await portal.insert()
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

    async def create_matrix_room(self, source: Puppet, participants: List[User]=None):
        assert self.wazo_uuid
        if self.mxid:
            # room already exists
            return self.mxid
        intent = source.intent

        # actually create a new matrix room
        room_id = await intent.create_room(invitees=participants and [
            p.mxid for p in participants
        ])
        self.mxid = room_id

        self.by_mxid[room_id] = self
        return room_id

