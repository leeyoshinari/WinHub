#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Request
from litestar.exceptions import HTTPException
from settings import TOKENs
from mycloud.models import SessionBase


# 校验用户是否登陆，返回用户名
# 从 cookie 中校验
async def auth(request: Request) -> SessionBase:
    username = request.cookies.get("u", '')
    lang = request.headers.get('lang', 'en')
    ip = request.headers.get('x-real-ip', '')
    token = request.cookies.get("token", None)
    groupname = request.cookies.get("g", '')
    if not username or username not in TOKENs or token != TOKENs[username]:
        raise HTTPException(status_code=401)
    return SessionBase(username=username, groupname=groupname, ip=ip, lang=lang)


# 从 url 中校验
async def auth_url(request: Request) -> SessionBase:
    username = request.query_params.get('u', '')
    groupname = request.query_params.get('g', '')
    lang = request.query_params.get('lang', 'en')
    ip = request.headers.get('x-real-ip', '')
    token = request.query_params.get("token", None)
    if not username or username not in TOKENs or token != TOKENs[username]:
        raise HTTPException(status_code=401)
    return SessionBase(username=username, groupname=groupname, ip=ip, lang=lang)


# # 从 cookie 或 url 中校验，用于既有 cookie 又有 url 校验的场景
# def auth_uc(request: Request) -> SessionBase:
#     username = request.query_params.get('u', None)
#     lang = request.query_params.get('lang', None)
#     ip = request.headers.get('x-real-ip', '')
#     token = request.query_params.get("token", None)
#     if not username or not lang or not token:
#         username = request.cookies.get("u", 's')
#         lang = request.headers.get('lang', 'en')
#         token = request.cookies.get("token", None)
#     if not username or username not in TOKENs or token != TOKENs[username]:
#         raise HTTPException(status_code=401)
#     return SessionBase(username=username, ip=ip, lang=lang)


# 不校验，只获取信息
async def no_auth(request: Request) -> SessionBase:
    username = request.query_params.get('u', '')
    groupname = request.query_params.get('g', '')
    lang = request.query_params.get('lang', 'en')
    if not username or not lang:
        username = request.cookies.get("u", '')
        groupname = request.cookies.get("g", '')
        lang = request.headers.get('lang', 'en')
    ip = request.headers.get('x-real-ip', '')
    return SessionBase(username=username, groupname=groupname, ip=ip, lang=lang)
