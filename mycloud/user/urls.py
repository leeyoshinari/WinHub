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
from settings import BASE_PATH, ROOT_PATH, SECRET_KEY
import jwt


class UserContoller(Controller):
    path = "/user"
    tags = ['user (用户管理)']
    dependencies = {"hh": Provide(auth), "hh_no": Provide(no_auth)}

    @get("/status", summary="Get login status (获取用户登录状态)")
    async def get_status(self, request: Request) -> Result:
        token = request.cookies.get("token", None)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = await User.get(payload['username'])
            return Result(data=user.nickname)
        except:
            logger.warning(f"获取用户登录状态失败: {traceback.format_exc()}")
            return Result(code=-1)

    @post("/create/group", summary="Create group (创建用户组)")
    async def create_group(self, group_name: str, hh_no: models.SessionBase) -> Result:
        result = Result()
        try:
            group = await Group.get(group_name.strip())
            if group:
                result.code = 1
                result.msg = Msg.FileExist.get_text(hh_no.lang).format(group_name)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            group = await Group.create2return(id=group_name)
            try:
                for k, v in ROOT_PATH.items():
                    folder = await FileExplorer.get(k)
                    if not folder:
                        await FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = await FileExplorer.get(f"{k}{group.id}")
                    if not folder:
                        await FileExplorer.create(id=f"{k}{group.id}", name=group.id, parent_id=k, format='ffolder', username='system')
                    user_path = os.path.join(v, group.id)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
            except:
                await Group.query().equal(id=group.id).delete()
                result.code = 1
                result.msg = f"{Msg.Create.get_text(hh_no.lang).format(group_name)}{Msg.Failure.get_text(hh_no.lang)}"
                logger.error(traceback.format_exc())
                return result
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
                group = await Group.get_one(groupname)
            except:
                result.code = 1
                result.msg = Msg.FileNotExist.get_text(hh_no.lang).format(groupname)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            user = await User.get(username.strip())
            if user:
                result.code = 1
                result.msg = Msg.ExistUserError.get_text(hh_no.lang).format(username)
                logger.error(f"{result.msg}, IP: {hh_no.ip}")
                return result
            password = str_md5(password)
            user = await User.create2return(nickname=nickname, id=username, password=password, group_id=group.id)
            try:
                for k, v in ROOT_PATH.items():
                    folder = await FileExplorer.get(k)
                    if not folder:
                        await FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = await FileExplorer.get(f"{k}{user.group_id}")
                    if not folder:
                        await FileExplorer.create(id=f"{k}{user.group_id}", name=user.group_id, parent_id=k, format='ffolder', username='system')
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
                await User.query().equal(id=user.id).delete()
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
            user = await User.get(data.username)
            await User.update(user.id, password=str_md5(parse_pwd(data.password, data.t)))
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
            user = await User.get(hh.username)
            await User.update(user.id, nickname=nickname)
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
            user = await User.get(data.username)
            if user and user.password == str_md5(parse_pwd(data.password, data.t)):
                for k, v in ROOT_PATH.items():
                    folder = await FileExplorer.get(k)
                    if not folder:
                        await FileExplorer.create(id=k, parent=None, name=v, format='ffolder', username='system')
                    folder = await FileExplorer.get(f"{k}{user.group_id}")
                    if not folder:
                        await FileExplorer.create(id=f"{k}{user.group_id}", name=user.group_id, parent_id=k, format='ffolder', username='system')
                    user_path = os.path.join(v, user.group_id)
                    if not os.path.exists(user_path):
                        os.mkdir(user_path)
                token_dict = {'username': user.id, 'groupname': user.group_id, 'nickname': user.nickname, 'exp': time.time() + 36000}
                token = jwt.encode(token_dict, SECRET_KEY, algorithm="HS256")
                response = Response(Result().__dict__)
                response.set_cookie('token', token)
                response.set_cookie('u', user.id)
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
        response = Response(Result().__dict__)
        response.set_cookie('token', None)
        logger.info(f"{Msg.Logout.get_text(hh.lang).format(hh.username)}{Msg.Success.get_text(hh.lang)}, IP: {hh.ip}")
        return response

    @get("/list", summary="Users list（用户列表）")
    async def user_list(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            users = await User.query().all()
            result.data = [models.UserList.from_orm_format(f).model_dump() for f in users if f.group_id == hh.groupname and f.id == hh.username] + [models.UserList.from_orm_format(f).model_dump() for f in users if f.group_id == hh.groupname and f.id != hh.username]
            logger.info(Msg.CommonLog.get_text(hh.lang).format("user list", hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result

    @post("/delete", summary="Delete user（删除用户）")
    async def delete_user(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            user = await User.get_one(hh.username)
            await User.query().equal(id=user.id).delete()
            logger.info(Msg.CommonLog1.get_text(hh.lang).format("Delete user", hh.username, hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result

    @get("/group/list", summary="Group list（用户组列表）")
    async def group_list(self, hh: models.SessionBase) -> Result:
        result = Result()
        try:
            groups = await Group.query().all()
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
            users = await User.query().equal(group_id=groupname).all()
            result.data = [models.UserList.from_orm_format(f).model_dump() for f in users]
            logger.info(Msg.CommonLog.get_text(hh.lang).format("Group list", hh.username, hh.ip))
        except:
            logger.error(traceback.format_exc())
            result.code = 0
        return result
