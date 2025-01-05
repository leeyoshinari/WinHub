#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from mycloud import models
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def get_rank(game_type: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        game = await models.Games.filter(type=game_type).order_by('-score').limit(5)
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
        game = await models.Games.filter(type=query.type, name=hh.username)
        if game:
            if game[0].score < query.score:
                game[0].score = query.score
                await game[0].save()
            else:
                result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Success.get_text(hh.lang))
        else:
            _ = await models.Games.create(type=query.type, name=hh.username, score=query.score)
        result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Success.get_text(hh.lang))
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, f'{query.type}-{query.score}', hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.GameScore.get_text(hh.lang).format(Msg.Failure.get_text(hh.lang))
        logger.error(traceback.format_exc())
    return result
