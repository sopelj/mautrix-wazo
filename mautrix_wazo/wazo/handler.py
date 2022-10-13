from __future__ import annotations
from logging import Logger
from typing import TYPE_CHECKING

from mautrix_wazo.portal import Portal
from mautrix_wazo.puppet import Puppet
from mautrix_wazo.types import WazoMessage
from mautrix_wazo.user import User

if TYPE_CHECKING:
    from mautrix_wazo.__main__ import WazoBridge

"""
{
    "uuid": "29329334-7659-45c9-ab34-f1a51c8722d1",
    "content": "toto",
    "alias": null,
    "user_uuid": "425d3fcd-22d4-4621-a1f0-dc71d0d3a4ce",
    "tenant_uuid": "47bfdafc-2897-4369-8fb3-153d41fb835d",
    "wazo_uuid": "2170f276-9344-44e8-aad7-dd98bb849b8f",
    "created_at": "2022-10-12T19:55:14.283053+00:00",
    "room": {
      "uuid": "1930d6e1-cfb7-407d-bd9c-439b8b501e61"
    },
    "participants": [
      "13ba3c26-049d-4e14-a6e7-ac08d9cc8ecd",
      "0579bb74-c7e4-4c17-9f41-7dc2ab067efa",
      "4a76e207-5423-4b75-b4ea-ce5f99b52196",
      "425d3fcd-22d4-4621-a1f0-dc71d0d3a4ce"
    ]
}
"""


class WazoWebhookHandler:
    """
    Handle webhook for events dispatched by wazo
    """
    logger: Logger
    bridge: WazoBridge

    def __init__(self, logger: Logger, bridge):
        self.logger = logger
        self.bridge = bridge

    async def handle_message(self, message: WazoMessage):
        # get portal representing room
        # TODO: logic for creating matrix room if missing?

        # get matrix side puppet for the sender
        sender_puppet = await Puppet.get_by_uuid(message.sender_id, create=True)
        if sender_puppet.mxid:
            self.logger.info("Message sender: (wazo id %s, matrix id %s)", sender_puppet.wazo_uuid, sender_puppet.mxid)

        portal: Portal = await Portal.get_by_wazo_id(message.room_id, create=True)

        mapped_participants = [
            await User.get_by_uuid(p)
            for p in message.participants
        ]
        if not any(mapped_participants):
            self.logger.info("No participant in room has an associated matrix id. Ignoring.")
            # if no participant has a matrix user, we can ignore
            return

        # setup
        puppets = [
            await Puppet.get_by_uuid(p)
            for p in message.participants
        ]
        if not portal.mxid:
            try:
                admin_user = next(p for p in mapped_participants if p)
            except StopIteration:
                # no registered matrix user in participants, this is a failure case
                raise Exception("No registered matrix user in participants for message")
            else:
                # create a new matrix room with participants
                room_id = await portal.create_matrix_room(source=admin_user, participants=[
                    p.mxid for p in puppets if p.mxid
                ], name=":".join(pup.first_name for pup in puppets))
                self.logger.info("Created corresponding matrix room(%s)", room_id)

        event_id = await portal.handle_wazo_message(puppet=sender_puppet, message=message)
        self.logger.info("Dispatched wazo message to matrix (event id %s)", event_id)

        # wazo message should have been dispatched to matrix
        # TODO: anything else?







