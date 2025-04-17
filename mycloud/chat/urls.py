#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import traceback
from litestar import Controller, get, WebSocket, websocket
from litestar.exceptions import WebSocketDisconnect
from litestar.di import Provide
from mycloud import models
from mycloud.auth_middleware import auth
from mycloud.chat import views
from common.results import Result
from common.logging import logger


rooms = {}


class ChatController(Controller):
    path = "/chat"
    tags = ['Chat (音视频聊天)']
    dependencies = {"hh": Provide(auth)}

    @get("/list", summary="Chat records list (聊天记录列表)")
    async def chat_list(self, hh: models.SessionBase) -> Result:
        result = await views.get_room_list(hh)
        return result

    @get("/create/{chat_mode: int}", summary="Create code (创建房间码)")
    async def create_code(self, chat_mode: int, hh: models.SessionBase) -> Result:
        result = await views.create_code(chat_mode, hh)
        return result

    @get("/auth/{chat_mode: int}/{room_code: str}", summary="Start Chat (开始聊天)")
    async def auth_chat(self, chat_mode: int, room_code: str, hh: models.SessionBase) -> Result:
        result = await views.start_chat(room_code, chat_mode, hh)
        return result

    @get("/stun/{room_code: str}", summary="Get stun & turn (获取stun & turn)")
    async def chat_stun(self, room_code: str, hh: models.SessionBase) -> Result:
        result = await views.get_stun_server(room_code, hh)
        return result

    @websocket('/join/{username: str}/{room_code: str}')
    async def start_chat(self, websocket: WebSocket, username: str, room_code: str) -> None:
        await websocket.accept()
        try:
            if not views.is_auth(room_code, websocket, username):
                await websocket.close()
                return
            while True:
                data = await websocket.receive_text()
                await views.broadcast(room_code, data, websocket)
        except WebSocketDisconnect:
            logger.error("websocket disconnected.")
        except:
            logger.error(traceback.format_exc())
            await websocket.close()
        finally:
            await views.leave_room(room_code, websocket, username)
