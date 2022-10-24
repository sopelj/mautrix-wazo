from __future__ import annotations
from logging import Logger
from typing import TYPE_CHECKING

from mautrix_wazo.portal import Portal
from mautrix_wazo.puppet import Puppet
from mautrix_wazo.types import WazoMessage
from mautrix_wazo.user import User

if TYPE_CHECKING:
    from mautrix_wazo.__main__ import WazoBridge


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

        portal: Portal = await Portal.get_by_wazo_id(message.room_id, create=True)

        mapped_participants = [
            user
            for p in message.participants
            if (user := await User.get_by_uuid(p))
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
                participants_mxids = [
                    p.mxid for p in puppets if p.mxid
                ]
                self.logger.debug("participants")
                assert admin_user.mxid in participants_mxids
                # create a new matrix room with participants
                room_id = await portal.create_matrix_room(source=admin_user, participants=participants_mxids,
                                                          name=":".join(pup.first_name for pup in puppets))
                self.logger.info("Created corresponding matrix room(%s)", room_id)

        try:
            sender_matrix_user = next(u for u in mapped_participants if (u.wazo_uuid == message.sender_id))
            assert sender_matrix_user.mxid
        except StopIteration:
            sender_puppet = await Puppet.get_by_uuid(message.sender_id, create=True)
            self.logger.info("Sender(wazo id %s) has no custom matrix user registered, using auto-generated user(mxid %s)",
                             message.sender_id, sender_puppet.mxid)
        else:
            sender_puppet = await Puppet.get_by_custom_mxid(sender_matrix_user.mxid)
            self.logger.info(
                "Sender(wazo id %s) has custom matrix user registered(mxid %s)!",
                message.sender_id, sender_puppet.mxid)

        assert sender_puppet.mxid
        self.logger.info("Message sender: (wazo id %s, matrix id %s)", sender_puppet.wazo_uuid, sender_puppet.mxid)

        event_id = await portal.handle_wazo_message(puppet=sender_puppet, message=message)
        self.logger.info("Dispatched wazo message to matrix (event id %s)", event_id)








