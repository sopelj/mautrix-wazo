from __future__ import annotations

from typing import TYPE_CHECKING

from mautrix.bridge import BaseMatrixHandler
from mautrix.types import RoomID, UserID, EventID

from .user import User

if TYPE_CHECKING:
    from .__main__ import WazoBridge


class MatrixHandler(BaseMatrixHandler):
    def __init__(self, bridge: WazoBridge) -> None:
        prefix, suffix = bridge.config["bridge.username_template"].format(userid=":").split(":")
        homeserver = bridge.config["homeserver.domain"]
        self.user_id_prefix = f"@{prefix}"
        self.user_id_suffix = f"{suffix}:{homeserver}"

        super().__init__(bridge=bridge)

    async def send_welcome_message(self, room_id: RoomID, inviter: User) -> None:
        pass

    async def handle_leave(self, room_id: RoomID, user_id: UserID, event_id: EventID) -> None:
        pass
