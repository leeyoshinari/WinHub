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
from mycloud.SSH.urls import ServerController
from mycloud.share.urls import ShareController
from mycloud.music.urls import MusicController
from mycloud.health.urls import HealthController
from mycloud.database import Database
# import mycloud.music.urls as music_urls
# import mycloud.games.urls as game_urls
# import mycloud.system.urls as system_urls
# import mycloud.karaoke.urls as karaoke_urls
# import mycloud.downloader.urls as downloader_urls
# import mycloud.onlyoffice.urls as onlyoffice_urls
# import mycloud.backup.urls as backup_urls
# import mycloud.chat.urls as chat_urls
# import mycloud.health.urls as health_urls


Database.init_db()
modify_prefix(PREFIX)   # 将后端的 prefix 写入前端变量中
modify_sw()     # 修改 sw.js 文件中的缓存版本号
modify_manifest(PWA_URL)    # 修改 manifest.json 文件中的 url
route_handlers = [
    Router(path=PREFIX, route_handlers=[UserContoller]),
    Router(path=PREFIX, route_handlers=[FolderController]),
    Router(path=PREFIX, route_handlers=[FileController]),
    Router(path=PREFIX, route_handlers=[ShareController]),
    Router(path=PREFIX, route_handlers=[MusicController]),
    Router(path=PREFIX, route_handlers=[ServerController]),
    Router(path=PREFIX, route_handlers=[HealthController]),
]


@asynccontextmanager
async def lifespan(app: Litestar):
    scheduler.start()
    yield
    scheduler.shutdown()

render_file = SwaggerRenderPlugin(js_url=f'{FRONT_END_PREFIX}/js/swagger-ui-bundle.js', css_url=f'{FRONT_END_PREFIX}/css/swagger-ui.css')
openapi_config = OpenAPIConfig(title="WinHub", version="1.0", description="This is API of WinHub.", path=PREFIX + "/schema", render_plugins=[render_file])
app = Litestar(route_handlers=route_handlers, openapi_config=openapi_config, lifespan=[lifespan])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=False)
