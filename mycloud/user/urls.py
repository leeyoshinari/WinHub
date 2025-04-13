#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import time
import shutil
import traceback
from litestar import Controller, get, post, Request, Response
from litestar.di import Provide
from mycloud import models
from mycloud.database import User, FileExplorer
from mycloud.auth_middleware import auth, no_auth
from common.calc import str_md5, parse_pwd
from common.results import Result
from common.logging import logger
from common.messages import Msg
from settings import BASE_PATH, TOKENs, ROOT_PATH


class UserContoller(Controller):
    path = "/user"
    tags = ['user (用户管理)']
    dependencies = {"hh": Provide(auth), "hh_no": Provide(no_auth)}

    @get("/status", summary="Get login status (获取用户登录状态)")
    async def get_status(self, request: Request) -> Result:
        username = request.cookies.get("u", 's')
        token = request.cookies.get("token", None)
        if not username or username not in TOKENs or token != TOKENs[username]:
            return Result(code=-1)
        user = User.get(username)
        return Result(data=user.nickname)

    @get("/test/createUser", summary="Create user (创建用户)")
    async def create_user(self, username: str, nickname: str, password: str, password1: str, hh_no: models.SessionBase) -> Result:
        result = Result()
        try:
            if not username.isalnum():
                result.code = 1
                result.msg = Msg.UserCheckUsername.get_text(hh_no.lang)
                return result
            if password != password1:
                result.code = 1
                result.msg = Msg.UserCheckPassword.get_text(hh_no.lang)
                return result
            user = User.get(username.strip())
            if user:
                result.code = 1
                result.msg = Msg.ExistUserError.get_text(hh_no.lang).format(username)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            password = str_md5(password)
            user = User.create(nickname=nickname, username=username, password=password)
            for k, v in ROOT_PATH.items():
                folder = FileExplorer.get(k)
                if not folder:
                    FileExplorer.create(id=k, parent=None, name=v, format='folder', username='system')
                folder = FileExplorer.get(f"{k}{user.username}")
                if not folder:
                    FileExplorer.create(id=f"{k}{user.username}", name=user.username, parent_id=k, format='folder', username='system')
                user_path = os.path.join(v, user.username)
                if not os.path.exists(user_path):
                    os.mkdir(user_path)
            back_path = os.path.join(BASE_PATH, 'web/img/pictures', user.username)
            if not os.path.exists(back_path):
                os.mkdir(back_path)
            source_file = os.path.join(BASE_PATH, 'web/img/pictures/undefined/background.jpg')
            target_file = os.path.join(back_path, 'background.jpg')
            login_file = os.path.join(back_path, 'login.jpg')
            shutil.copy(source_file, target_file)
            shutil.copy(source_file, login_file)
            result.msg = f"{Msg.CreateUser.get_text(hh_no.lang).format(user.username)}{Msg.Success.get_text(hh_no.lang)}"
            logger.info(f"{result.msg}, IP: {hh_no.ip}")
        except:
            result.code = 1
            result.msg = f"{Msg.CreateUser.get_text(hh_no.lang).format(username)}{Msg.Failure.get_text(hh_no.lang)}"
            logger.error(traceback.format_exc())
        return result

    @post("/modify/pwd", summary="Modify password (修改用户密码)")
    async def modify_pwd(self, data: models.CreateUser, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            if data.password != data.password1:
                result.code = 1
                result.msg = Msg.UserCheckPassword.get_text(hh.lang)
                return result
            user = User.get(data.username)
            User.update(user, password=str_md5(parse_pwd(data.password, data.t)))
            result.msg = f"{Msg.ModifyPwd.get_text(hh.lang).format(user.username)}{Msg.Success.get_text(hh.lang)}"
            logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        except:
            result.code = 1
            result.msg = f"{Msg.ModifyPwd.get_text(hh.lang).format(data.username)}{Msg.Failure.get_text(hh.lang)}"
            logger.error(traceback.format_exc())
        return result

    @get("/modify/nickname", summary="Modify nickname (修改昵称)")
    async def modify_nickname(self, nickname: str, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            user = User.get(hh.username)
            user = User.update(user, nickname=nickname)
            result.data = nickname
            result.msg = f"{Msg.ModifyStr.get_text(hh.lang).format(user.nickname)}{Msg.Success.get_text(hh.lang)}"
            logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        except:
            result.code = 1
            result.msg = f"{Msg.ModifyStr.get_text(hh.lang).format(hh.username)}{Msg.Failure.get_text(hh.lang)}"
            logger.error(traceback.format_exc())
        return result

    @post("/login", summary="Login (用户登陆)")
    async def login(self, data: models.UserBase, hh_no: models.SessionBase) -> Result:
        result = Result()
        try:
            user = User.get(data.username)
            if user and user.password == str_md5(parse_pwd(data.password, data.t)):
                for k, v in ROOT_PATH.items():
                    folder = FileExplorer.get(k)
                    if not folder:
                        FileExplorer.create(id=k, parent=None, name=v, format='folder', username='system')
                    folder = FileExplorer.get(f"{k}{user.username}")
                    if not folder:
                        FileExplorer.create(id=f"{k}{user.username}", name=user.username, parent_id=k, format='folder', username='system')
                    user_path = os.path.join(v, user.username)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
                pwd_str = f'{time.time()}_{user.username}_{int(time.time())}_{user.nickname}'
                token = str_md5(pwd_str)
                TOKENs.update({user.username: token})
                response = Response(Result().__dict__)
                response.set_cookie('u', user.username)
                response.set_cookie('t', str(int(time.time() / 1000)))
                response.set_cookie('token', token)
                result.data = user.nickname
                result.msg = f"{Msg.Login.get_text(hh_no.lang).format(user.username)}{Msg.Success.get_text(hh_no.lang)}"
                logger.info(f"{result.msg}, IP: {hh_no.ip}")
                return response
            else:
                result.code = 1
                result.msg = Msg.LoginUserOrPwdError.get_text(hh_no.lang)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
        except:
            result.code = 1
            result.msg = f"{Msg.Login.get_text(hh_no.lang).format(data.username)}{Msg.Failure.get_text(hh_no.lang)}"
            logger.error(traceback.format_exc())
        return result

    @get("/logout", summary="Logout (退出登陆)")
    async def logout(self, hh: models.SessionBase) -> Result:
        TOKENs.pop(hh.username, 0)
        logger.info(f"{Msg.Logout.get_text(hh.lang).format(hh.username)}{Msg.Success.get_text(hh.lang)}, IP: {hh.ip}")
        return Result()
