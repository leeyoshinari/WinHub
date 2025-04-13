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
    # def __init__(self, code=0, msg='Success!', data=None, total=0):
    #     self.code = code
    #     self.msg = msg
    #     self.data = data
    #     self.total = total
