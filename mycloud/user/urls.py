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
from mycloud.database import Group, User, FileExplorer
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

    @post("/create/group", summary="Create group (创建用户组)")
    async def create_group(self, group_name: str, hh_no: models.SessionBase) -> Result:
        result = Result()
        try:
            group = Group.get(group_name.strip())
            if group:
                result.code = 1
                result.msg = Msg.FileExist.get_text(hh_no.lang).format(group_name)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            group = Group.create(id=group_name)
            try:
                for k, v in ROOT_PATH.items():
                    folder = FileExplorer.get(k)
                    if not folder:
                        FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = FileExplorer.get(f"{k}{group.id}")
                    if not folder:
                        FileExplorer.create(id=f"{k}{group.id}", name=group.id, parent_id=k, format='ffolder', username='system')
                    user_path = os.path.join(v, group.id)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
            except:
                Group.delete(group)
                logger.error(traceback.format_exc())
            result.msg = f"{Msg.Create.get_text(hh_no.lang).format(group.id)}{Msg.Success.get_text(hh_no.lang)}"
            logger.info(f"{result.msg}, IP: {hh_no.ip}")
        except:
            result.code = 1
            result.msg = f"{Msg.Create.get_text(hh_no.lang).format(group_name)}{Msg.Failure.get_text(hh_no.lang)}"
            logger.error(traceback.format_exc())
        return result

    @post("/create/user", summary="Create user (创建用户)")
    async def create_user(self, groupname: str, username: str, nickname: str, password: str, password1: str, hh_no: models.SessionBase) -> Result:
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
            try:
                group = Group.get_one(groupname)
            except:
                result.code = 1
                result.msg = Msg.FileNotExist.get_text(hh_no.lang).format(groupname)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            user = User.get(username.strip())
            if user:
                result.code = 1
                result.msg = Msg.ExistUserError.get_text(hh_no.lang).format(username)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            password = str_md5(password)
            user = User.create(nickname=nickname, id=username, password=password, group_id=group.id)
            try:
                for k, v in ROOT_PATH.items():
                    folder = FileExplorer.get(k)
                    if not folder:
                        FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = FileExplorer.get(f"{k}{user.group_id}")
                    if not folder:
                        FileExplorer.create(id=f"{k}{user.group_id}", name=user.group_id, parent_id=k, format='ffolder', username='system')
                    user_path = os.path.join(v, user.group_id)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
                back_path = os.path.join(BASE_PATH, 'web/img/pictures', user.id)
                if not os.path.exists(back_path):
                    os.mkdir(back_path)
                source_file = os.path.join(BASE_PATH, 'web/img/pictures/undefined/background.jpg')
                target_file = os.path.join(back_path, 'background.jpg')
                login_file = os.path.join(back_path, 'login.jpg')
                shutil.copy(source_file, target_file)
                shutil.copy(source_file, login_file)
            except:
                User.delete(user)
                logger.error(traceback.format_exc())
            result.msg = f"{Msg.CreateUser.get_text(hh_no.lang).format(user.id)}{Msg.Success.get_text(hh_no.lang)}"
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
            result.msg = f"{Msg.ModifyPwd.get_text(hh.lang).format(user.id)}{Msg.Success.get_text(hh.lang)}"
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
                        FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = FileExplorer.get(f"{k}{user.group_id}")
                    if not folder:
                        FileExplorer.create(id=f"{k}{user.group_id}", name=user.group_id, parent_id=k, format='ffolder', username='system')
                    user_path = os.path.join(v, user.group_id)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
                pwd_str = f'{time.time()}_{user.id}_{int(time.time())}_{user.group_id}'
                token = str_md5(pwd_str)
                TOKENs.update({user.id: token})
                response = Response(Result().__dict__)
                response.set_cookie('u', user.id)
                response.set_cookie('t', str(int(time.time() / 1000)))
                response.set_cookie('token', token)
                response.set_cookie('g', user.group_id)
                result.data = user.nickname
                result.msg = f"{Msg.Login.get_text(hh_no.lang).format(user.id)}{Msg.Success.get_text(hh_no.lang)}"
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

    @get("/list", summary="Users list（用户列表）")
    async def user_list(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            users = User.all().all()
            result.data = [models.UserList.from_orm_format(f).model_dump() for f in users]
            logger.info(Msg.CommonLog.get_text(hh.lang).format("user list", hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result

    @post("/delete", summary="Delete user（删除用户）")
    async def delete_user(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            user = User.get_one(hh.username)
            User.delete(user)
            logger.info(Msg.CommonLog1.get_text(hh.lang).format("Delete user", hh.username, hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result

    @get("/group/list", summary="Group list（用户组列表）")
    async def group_list(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            groups = Group.all().all()
            result.data = [models.GroupList.from_orm_format(f).model_dump() for f in groups]
            logger.info(Msg.CommonLog.get_text(hh.lang).format("Group list", hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result

    @get("/group/user", summary="User list of Group（用户组下的用户列表）")
    async def group_user(self, groupname: str, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            users = User.query(group_id=groupname).all()
            result.data = [models.UserList.from_orm_format(f).model_dump() for f in users]
            logger.info(Msg.CommonLog.get_text(hh.lang).format("Group list", hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result
