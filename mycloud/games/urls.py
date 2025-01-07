#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.games import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/games', tags=['games (游戏)'], responses={404: {'description': 'Not found'}})


@router.get("/get/rank/{game_type}", summary="get game ranking (获取游戏排名)")
async def get_rank(game_type: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_rank(game_type, hh)
    return result


@router.post("/set/score", summary="set game score (设置游戏得分)")
async def set_score(query: models.GamesScoreInfo, hh: models.SessionBase = Depends(auth)):
    result = await views.set_score(query, hh)
    return result
