from typing import Any, List

from mautrix import bridge as br
from mautrix.bridge import BasePortal, BasePuppet
from mautrix.types import MessageEventContent, EventID

from .db.portal import Portal as DBPortal
from .types import WazoMessage, WazoUserId
from .user import User
from .wazo.handler import WazoRoomId


class Store:
    """
    Global state storage wrapper
    """
    _wazo_rooms: dict
    _users: dict

    def get_portal(self, wazo_room_id) -> Portal:
        return self._wazo_rooms[wazo_room_id]


class PortalFailure(Exception):
    pass


class Portal(DBPortal, BasePortal):
    async def save(self) -> None:
        pass

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

    async def delete(self) -> None:
        pass

    @classmethod
    async def get_by_wazo_room_id(cls, room_id: WazoRoomId, create=True):
        try:
            return await cls.store.get_portal(dict(wazo_room_id=room_id))
        except KeyError:
            if create:
                portal = cls()
                return cls.store.add_portal(portal)
            else:
                raise PortalFailure

    async def handle_wazo_message(self, sender: User, message: WazoMessage):
        await self.create_matrix_room(participants=message.participants)

    async def create_matrix_room(self, participants: List[WazoUserId]):
        pass
