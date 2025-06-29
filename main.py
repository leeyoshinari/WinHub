#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Litestar, Router
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from contextlib import asynccontextmanager
from common.calc import modify_prefix, modify_sw, modify_manifest
from common.scheduler import scheduler
from settings import PREFIX, HOST, PORT, PWA_URL, FRONT_END_PREFIX
from mycloud.user.urls import UserContoller
from mycloud.files.urls import FileController
from mycloud.folders.urls import FolderController
from mycloud.system.urls import SystemController
from mycloud.SSH.urls import ServerController
from mycloud.share.urls import ShareController
from mycloud.music.urls import MusicController
from mycloud.downloader.urls import DownloaderController
from mycloud.onlyoffice.urls import OnlyofficeController
from mycloud.backup.urls import SyncController
from mycloud.chat.urls import ChatController
from mycloud.games.urls import GameController
from mycloud.karaoke.urls import KaraokeController
from mycloud.health.urls import HealthController
from mycloud.database import Database, init_data


Database.init_db()  # 初始化数据库
init_data()     # 数据库更新
modify_prefix(PREFIX)   # 将后端的 prefix 写入前端变量中
modify_sw()     # 修改 sw.js 文件中的缓存版本号
modify_manifest(PWA_URL)    # 修改 manifest.json 文件中的 url
route_handlers = [
    Router(path=PREFIX, route_handlers=[UserContoller]),
    Router(path=PREFIX, route_handlers=[FolderController]),
    Router(path=PREFIX, route_handlers=[FileController]),
    Router(path=PREFIX, route_handlers=[SystemController]),
    Router(path=PREFIX, route_handlers=[ShareController]),
    Router(path=PREFIX, route_handlers=[MusicController]),
    Router(path=PREFIX, route_handlers=[DownloaderController]),
    Router(path=PREFIX, route_handlers=[OnlyofficeController]),
    Router(path=PREFIX, route_handlers=[ServerController]),
    Router(path=PREFIX, route_handlers=[SyncController]),
    Router(path=PREFIX, route_handlers=[ChatController]),
    Router(path=PREFIX, route_handlers=[GameController]),
    Router(path=PREFIX, route_handlers=[KaraokeController]),
    Router(path=PREFIX, route_handlers=[HealthController]),
]


@asynccontextmanager
async def lifespan(app: Litestar):
    scheduler.start()
    yield
    scheduler.shutdown()

render_file = SwaggerRenderPlugin(js_url=f'{FRONT_END_PREFIX}/js/swagger-ui-bundle.js', css_url=f'{FRONT_END_PREFIX}/css/swagger-ui.css')
openapi_config = OpenAPIConfig(title="WinHub", version="1.0", description="This is API of WinHub.", path=PREFIX + "/schema", render_plugins=[render_file])
app = Litestar(route_handlers=route_handlers, openapi_config=openapi_config, lifespan=[lifespan], logging_config=None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=False)
