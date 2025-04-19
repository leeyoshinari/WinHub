#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from sqlalchemy import desc
from mycloud import models
from mycloud.database import Games
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def get_rank(game_type: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        game = Games.query(type=game_type).order_by(desc(Games.score)).limit(5).all()
        rank_list = [models.GamesRankInfo.model_validate(f).model_dump() for f in game]
        result.data = rank_list
        log_str = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        result.msg = hh.username
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(log_str, game_type, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def set_score(query: models.GamesScoreInfo, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        game = Games.query(type=query.type, name=hh.username).order_by(desc(Games.score)).all()
        if game:
            if game[0].score < query.score:
                Games.update(game[0], score=query.score)
            else:
                result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Success.get_text(hh.lang))
        else:
            _ = Games.create(type=query.type, name=hh.username, score=query.score)
        result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Success.get_text(hh.lang))
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, f'{query.type}-{query.score}', hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Failure.get_text(hh.lang))
        logger.error(traceback.format_exc())
    return result
