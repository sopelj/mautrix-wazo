import datetime
import os
from typing import List

from aiohttp import web
import pydantic
import uvicorn

from mautrix_wazo.wazo.handler import WazoWebhookHandler
from mautrix_wazo.types import WazoMessage, WazoUUID

app = web.Application()

class WazoRoomData(pydantic.BaseModel):
    uuid: str


class WazoHookMessageData(pydantic.BaseModel):
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
    uuid: str
    content: str
    participants: List[str]
    room: WazoRoomData
    created_at: datetime.datetime
    user_uuid: str


def wazo_handler_provider() -> WazoWebhookHandler:
    """
    Provide a WazoWebhookHandler instance
    :return:
    """
    # TODO: create&initialize
    return WazoWebhookHandler()


async def receive_message(request: web.Request):
    body = await request.json()
    data = WazoHookMessageData.parse_obj(body)
    app.logger.info("Received request")
    handler = wazo_handler_provider()
    # data = WazoHookMessageData.parse_obj(body)
    await handler.handle_message(WazoMessage(
        event_id=WazoUUID(data.uuid),
        sender_id=WazoUUID(data.user_uuid),
        room_id=WazoUUID(data.room.uuid),
        content=data.content,
        participants=[
            WazoUUID(p)
            for p in data.participants
        ],
        created_at=data.created_at,
    ))


app.add_routes([web.RouteDef("post", "/messages", receive_message, kwargs={})])

