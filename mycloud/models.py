#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import time
import os.path
from typing import Optional, List, Any
from tortoise import fields
from tortoise.models import Model
from pydantic import BaseModel
from common.calc import beauty_size, beauty_time, time2date, beauty_chat_status, beauty_chat_mode


# 用户数据库模型
class User(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    nickname = fields.CharField(max_length=16, description='昵称')
    username = fields.CharField(max_length=16, description='用户名')
    password = fields.CharField(max_length=32, description='密码')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'user'


# 文件夹数据库模型
class Catalog(Model):
    id = fields.CharField(max_length=16, pk=True, description='目录ID')
    parent = fields.ForeignKeyField('models.Catalog', on_delete=fields.CASCADE, null=True, related_name='catalog', description='目录父ID')
    name = fields.CharField(max_length=50, description='目录名')
    is_delete = fields.IntField(default=0, description='是否删除, 0-不删除, 1-删除')
    is_backup = fields.IntField(default=0, description='是否备份, 0-不备份, 1-备份')
    create_time = fields.DatetimeField(auto_now_add=True, description='Create time')
    update_time = fields.DatetimeField(auto_now=True, description='Update time')

    class Meta:
        table = 'catalog'

    async def get_all_path(self):
        paths = []
        curr_node = self
        while curr_node:
            paths.append(curr_node.name)
            curr_node = await curr_node.parent
        return '/'.join(paths[::-1])


# 文件数据库模型
class Files(Model):
    id = fields.CharField(max_length=16, pk=True, description='文件ID')
    name = fields.CharField(max_length=64, description='文件名')
    format = fields.CharField(max_length=16, null=True, description='文件格式')
    parent = fields.ForeignKeyField('models.Catalog', on_delete=fields.CASCADE, related_name='files', description='目录ID')
    size = fields.BigIntField(default=None, null=True, description='文件大小')
    md5 = fields.CharField(max_length=50, index=True, description='文件的MD5值')
    is_delete = fields.IntField(default=0, description='是否删除, 0-不删除, 1-删除')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True, index=True)

    class Meta:
        db_table = 'files'


# 文件分享数据库模型
class Shares(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    file_id = fields.CharField(max_length=16, description='文件ID')
    name = fields.CharField(max_length=50, description='文件名')
    path = fields.CharField(max_length=256, description='文件路径')
    format = fields.CharField(max_length=16, default=None, description='文件格式')
    times = fields.IntField(default=0, description='链接已打开次数')
    username = fields.CharField(max_length=16, description='用户名')
    total_times = fields.IntField(default=1, description='分享链接打开最大次数')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')

    class Meta:
        db_table = 'shares'


# 服务器文件
class Servers(Model):
    id = fields.CharField(max_length=16, pk=True, description='ID')
    host = fields.CharField(max_length=16, description='服务器ID')
    port = fields.IntField(default=22, description='端口')
    user = fields.CharField(max_length=16, description='用户名')
    pwd = fields.CharField(max_length=36, description='密码')
    system = fields.CharField(max_length=64, description='系统')
    cpu = fields.IntField(default=1, description='cpu逻辑核数')
    mem = fields.FloatField(default=0.1, description='内存G')
    disk = fields.CharField(max_length=8, description='磁盘大小')
    creator = fields.CharField(max_length=16, description='用户名')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'servers'


# 音乐播放记录
class Musics(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    file_id = fields.CharField(max_length=16, description='文件ID')
    name = fields.CharField(max_length=64, description='文件名')
    singer = fields.CharField(max_length=16, description='歌手')
    duration = fields.CharField(max_length=16, description='歌曲时长')
    username = fields.CharField(max_length=16, description='用户名')
    times = fields.IntField(default=1, description="播放次数")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'music'


# 游戏得分记录
class Games(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    type = fields.CharField(max_length=8, description='游戏类型')
    name = fields.CharField(max_length=16, description='用户名')
    score = fields.IntField(default=0, description="得分")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'games'


# 桌面快捷方式记录
class Shortcuts(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    file_id = fields.CharField(max_length=16, description='文件ID')
    name = fields.CharField(max_length=64, description='文件名')
    format = fields.CharField(max_length=16, description='文件格式')
    username = fields.CharField(max_length=16, description='用户名')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'shortcuts'


# 卡拉OK记录
class Karaoke(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    name = fields.CharField(max_length=64, description='文件名')
    status = fields.IntField(default=0, description='歌是否开始唱, 0-不可以, 1-可以')
    times = fields.IntField(default=0, description='K歌次数')
    is_sing = fields.IntField(default=0, description='歌是否唱过, 0-从没唱过, 1-点了没唱, 2-唱了, -1-正在唱')
    is_top = fields.IntField(default=0, description='是否置顶, 0-不置顶, 1-置顶')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'karaoke'


# 视频聊天记录
class ChatRoom(Model):
    id = fields.IntField(pk=True, generated=True, description='主键')
    code = fields.CharField(max_length=8, description='房间码')
    mode = fields.IntField(default=0, description='聊天模式, 0-语音聊天, 1-视频聊天, 2-文件传输')
    start_time = fields.IntField(default=0, description='聊天开始时间')
    end_time = fields.IntField(default=0, description='聊天结束时间')
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        db_table = 'chat_room'


# 登陆会话验证模型
class SessionBase(BaseModel):
    username: str
    ip: Optional[str] = None
    lang: str = 'en'


# 用户模型
class UserBase(BaseModel):
    t: str
    username: str
    password: str


# 新建用户
class CreateUser(UserBase):
    password1: str


# 搜索文件
class SearchItems(BaseModel):
    q: Optional[str] = None
    sort_field: str = 'update_time'
    sort_type: str = 'desc'
    page: int = 1
    page_size: int = 20


# 新建文件、文件夹
class CatalogBase(BaseModel):
    id: str
    file_type: str


# 文件、文件夹移动模型
class CatalogMoveTo(BaseModel):
    from_ids: List[str]
    parent_id: str
    to_id: str


# 查询目录模型
class CatalogGetInfo(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


# 文件夹列表
class FolderList(BaseModel):
    id: str
    name: str
    folder_type: str = 'folder'
    format: str = ""
    size: int = 0
    create_time: str
    update_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Catalog):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(id=obj.id, name=obj.name, create_time=c, update_time=m)


# 重命名文件、文件夹
class FilesBase(BaseModel):
    id: str
    name: str


# 文件列表
class FileList(BaseModel):
    id: str
    name: str
    folder_type: str = 'file'
    format: str
    size: str
    create_time: str
    update_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Files):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(id=obj.id, name=obj.name, format=obj.format, size=beauty_size(obj.size), create_time=c, update_time=m)


# 文件下载模型
class DownloadFile(BaseModel):
    ids: List[str]
    file_type: str = "file"


# 文件保存模型
class SaveFile(BaseModel):
    id: str
    data: Any


# 文件删除模型
class IsDelete(BaseModel):
    ids: List[Any]
    file_type: str = "file"
    is_delete: int = 1
    delete_type: int = 0


# 文件分享模型
class ShareFile(BaseModel):
    id: str
    times: int


# 分享文件列表模型
class ShareFileList(BaseModel):
    id: int
    name: str
    format: str
    times: int
    total_times: int
    create_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Shares):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(id=obj.id, name=obj.name, format=obj.format, create_time=c, times=obj.times, total_times=obj.total_times)


# 本地文件导入模型
class ImportLocalFileByPath(BaseModel):
    id: str
    path: str


# 服务器模型
class ServerModel(BaseModel):
    t: str
    host: str
    port: int
    user: str
    pwd: str


# 服务器列表
class ServerListModel(BaseModel):
    id: str
    host: str
    port: int
    user: str
    system: str
    cpu: int
    mem: float
    disk: str

    class Config:
        from_attributes = True


# MP3列表
class MP3List(BaseModel):
    id: str
    name: str
    format: str
    size: str
    duration: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Files, duration):
        return cls(id=obj.id, name=obj.name, format=obj.format, size=beauty_size(obj.size), duration=duration)


# mp3 歌曲列表模型
class MusicList(BaseModel):
    file_id: str
    name: str
    singer: str
    duration: str
    create_time: str
    update_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Musics):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(file_id=obj.file_id, name=obj.name, singer=obj.singer, duration=obj.duration, create_time=c, update_time=m)


# 听歌历史记录模型
class MusicHistory(BaseModel):
    file_id: str
    name: str
    singer: str = ""
    duration: str


# aria2c 下载参数模型
class DownloadFileOnline(BaseModel):
    parent_id: str
    url: str
    cookie: Optional[str] = None


# aria2c 下载状态模型
class DownloadFileOnlineStatus(BaseModel):
    gid: str
    status: str


# aria2c 下载列表模型
class DownloadList(BaseModel):
    gid: str
    name: str
    path: str
    status: str
    completed_size: str
    total_size: str
    progress: float
    download_speed: str
    eta: str

    @classmethod
    def from_orm_format(cls, obj):
        files = [f['path'] for f in obj['files'] if f['selected'] == 'true']
        file_path = files[0]
        completed_length = int(obj['completedLength'])
        total_length = int(obj['totalLength'])
        download_speed = int(obj['downloadSpeed'])
        eta = beauty_time(int((total_length - completed_length) / download_speed)) if download_speed > 1 else '-'
        if total_length < 1:
            progress = 0
            eta = '-'
        else:
            progress = round((completed_length / total_length) * 100, 2)
        if download_speed < 1:
            eta = '-'

        return cls(gid=obj['gid'], name=file_path.split('/')[-1], path=file_path, status=obj['status'],
                   completed_size=beauty_size(completed_length), total_size=beauty_size(total_length), eta=eta,
                   download_speed=beauty_size(download_speed) + '/s', progress=progress)


# 游戏分数模型
class GamesScoreInfo(BaseModel):
    type: str
    score: int


# 游戏得分排序
class GamesRankInfo(BaseModel):
    name: str
    score: int

    class Config:
        from_attributes = True


# 快捷方式模型
class ShortCutsInfo(BaseModel):
    id: int
    file_id: str
    name: str
    format: str

    class Config:
        from_attributes = True


# 卡拉OK曲库列表
class KaraokeList(BaseModel):
    id: int
    name: str
    create_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj: Files):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        # m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        return cls(id=obj.id, name=obj.name, create_time=c)


# 卡拉OK历史记录
class KaraokeHistoryList(BaseModel):
    id: int
    name: str
    times: int
    is_sing: int
    is_top: int

    class Config:
        from_attributes = True


# BT 种子文件下载列表
class BtFileList(BaseModel):
    index: str
    gid: str
    size: str
    name: str
    path: str
    folder: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj, gid, folder_id):
        size = beauty_size(int(obj['length']))
        name = os.path.basename(obj['path'])
        return cls(gid=gid, index=obj['index'], size=size, name=name, path=obj['path'], folder=folder_id)


# 选择BT种子文件模型
class BtSelectedFiles(BaseModel):
    gid: str
    folder: str
    index: str


# 聊天记录模型
class ChatList(BaseModel):
    id: int
    code: str
    status: str
    mode: str
    duration: str
    start_time: str
    create_time: str
    update_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj, lang):
        status = 0
        duration = 0
        start_time = '-'
        if obj.start_time != 0:
            start_time = time2date(obj.start_time)
        if obj.start_time != 0 and obj.end_time == 0:
            status = 1
            duration = time.time() - obj.start_time
        if obj.end_time != 0:
            status = 2
            duration = obj.end_time - obj.start_time
        return cls(id=obj.id, code=obj.code, duration=beauty_time(duration), start_time=start_time, status=beauty_chat_status(status, lang), mode=beauty_chat_mode(obj.mode, lang),
                   create_time=obj.create_time.strftime("%Y-%m-%d %H:%M:%S"), update_time=obj.update_time.strftime("%Y-%m-%d %H:%M:%S"))
