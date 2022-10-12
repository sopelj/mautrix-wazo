from typing import Any

from mautrix import bridge as br
from mautrix.bridge import BasePortal, BasePuppet
from mautrix.types import MessageEventContent, EventID

from .db.portal import Portal as DBPortal


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