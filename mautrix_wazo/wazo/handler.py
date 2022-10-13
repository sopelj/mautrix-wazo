from mautrix_wazo.portal import Portal, PortalFailure
from mautrix_wazo.types import WazoMessage
from mautrix_wazo.user import User, UserError

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

    async def handle_message(self, message: WazoMessage):
        # get portal representing room
        # TODO: logic for creating matrix room if missing?
        try:
            portal: Portal = await Portal.get_by_wazo_id(message.room_id, create=True)
        except PortalFailure:
            raise

        # TODO: logic for creating matrix user if missing?
        try:
            sender: User = await User.get_by_wazo_id(message.sender_id, create=True)
        except UserError:
            raise

        await portal.handle_wazo_message(sender, message)
        # wazo message should have been dispatched to matrix
        # TODO: anything else







