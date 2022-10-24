import datetime
from typing import List

from aiohttp import web
import pydantic

from mautrix_wazo.wazo.handler import WazoWebhookHandler
from mautrix_wazo.types import WazoMessage, WazoUUID


class WazoRoomData(pydantic.BaseModel):
    uuid: str


class WazoHookMessageData(pydantic.BaseModel):
    uuid: str
    content: str
    participants: List[str]
    room: WazoRoomData
    created_at: datetime.datetime
    user_uuid: str
    proxied: bool


async def on_startup(app):
    app["wazo_handler"] = WazoWebhookHandler(logger=app.logger.getChild("."+WazoWebhookHandler.__name__),
                                             bridge=app["bridge"])


async def receive_message(request: web.Request):
    body = await request.json()
    data = WazoHookMessageData.parse_obj(body)
    request.app.logger.info("Received request")
    handler = request.app["wazo_handler"]
    if data.proxied:
        # message triggered by relayed matrix event, ignore
        return web.Response()

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
    return web.Response(status=200)


def init():
    app = web.Application()
    app.add_routes([web.RouteDef("post", "/messages", receive_message, kwargs={})])
    app.on_startup.append(on_startup)
    return app

