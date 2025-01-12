#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from tortoise.contrib.fastapi import register_tortoise
from common.calc import modify_prefix, modify_sw, modify_manifest
from common.scheduler import scheduler
from settings import PREFIX, TORTOISE_ORM, HOST, PORT, PWA_URL, FRONT_END_PREFIX
import mycloud.user.urls as user_urls
import mycloud.folders.urls as folder_urls
import mycloud.files.urls as file_urls
import mycloud.music.urls as music_urls
import mycloud.SSH.urls as ssh_urls
import mycloud.share.urls as share_urls
import mycloud.games.urls as game_urls
import mycloud.system.urls as system_urls
import mycloud.karaoke.urls as karaoke_urls
import mycloud.downloader.urls as downloader_urls
import mycloud.onlyoffice.urls as onlyoffice_urls
import mycloud.backup.urls as backup_urls
import mycloud.chat.urls as chat_urls


app = FastAPI(docs_url=None, redoc_url=None, root_path='/api/openapi')
register_tortoise(app=app, config=TORTOISE_ORM)
modify_prefix(PREFIX)   # 将后端的 prefix 写入前端变量中
modify_sw()     # 修改 sw.js 文件中的缓存版本号
modify_manifest(PWA_URL)    # 修改 manifest.json 文件中的 url


async def startup_event():
    scheduler.start()


@app.get(PREFIX + "/swagger-ui", include_in_schema=False)
async def get_docs():
    return get_swagger_ui_html(openapi_url='/api/openapi/openapi.json', title='Windows swagger-ui',
                               swagger_js_url=f'{FRONT_END_PREFIX}/js/swagger-ui-bundle.js', swagger_css_url=f'{FRONT_END_PREFIX}/css/swagger-ui.css')


app.include_router(user_urls.router, prefix=PREFIX)
app.include_router(folder_urls.router, prefix=PREFIX)
app.include_router(file_urls.router, prefix=PREFIX)
app.include_router(ssh_urls.router, prefix=PREFIX)
app.include_router(music_urls.router, prefix=PREFIX)
app.include_router(share_urls.router, prefix=PREFIX)
app.include_router(downloader_urls.router, prefix=PREFIX)
app.include_router(onlyoffice_urls.router, prefix=PREFIX)
app.include_router(game_urls.router, prefix=PREFIX)
app.include_router(system_urls.router, prefix=PREFIX)
app.include_router(karaoke_urls.router, prefix=PREFIX)
app.include_router(backup_urls.router, prefix=PREFIX)
app.include_router(chat_urls.router, prefix=PREFIX)
app.add_event_handler("startup", startup_event)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host=HOST, port=PORT, reload=False)
