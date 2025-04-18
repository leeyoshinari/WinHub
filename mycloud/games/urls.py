#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get, post
from litestar.di import Provide
from mycloud import models
from mycloud.games import views
from mycloud.auth_middleware import auth
from common.results import Result


class GameController(Controller):
    path = "/games"
    tags = ['games (游戏)']
    dependencies = {"hh": Provide(auth)}

    @get("/get/rank/{game_type: str}", summary="get game ranking (获取游戏排名)")
    async def get_rank(self, game_type: str, hh: models.SessionBase) -> Result:
        result = await views.get_rank(game_type, hh)
        return result

    @post("/set/score", summary="set game score (设置游戏得分)")
    async def set_score(self, data: models.GamesScoreInfo, hh: models.SessionBase) -> Result:
        result = await views.set_score(data, hh)
        return result
