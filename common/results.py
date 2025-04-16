#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from pydantic import BaseModel
from typing import Any


class Result(BaseModel):
    code: int = 0
    msg: str = 'Success!'
    data: Any = None
    total: int = 0
