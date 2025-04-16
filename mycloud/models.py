#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import time
import os.path
from typing import Optional, List, Any
from pydantic import BaseModel
from common.calc import beauty_size, beauty_time, time2date, beauty_chat_status, beauty_chat_mode


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
    format: str
    size: str
    create_time: str
    update_time: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_format(cls, obj):
        c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
        file_size = "0" if obj.format == 'folder' else beauty_size(obj.size)
        return cls(id=obj.id, name=obj.name, format=obj.format, size=file_size, create_time=c, update_time=m)


# 重命名文件、文件夹
class FilesBase(BaseModel):
    id: str
    name: str


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
    def from_orm_format(cls, obj):
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
    def from_orm_format(cls, obj, duration):
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
    def from_orm_format(cls, obj):
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
    file_name: Optional[str] = None
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

    # @classmethod
    # def from_orm_format(cls, obj: Files):
    #     c = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
    #     # m = obj.update_time.strftime("%Y-%m-%d %H:%M:%S")
    #     return cls(id=obj.id, name=obj.name, create_time=c)


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


# 设置健康数据
class HealthData(BaseModel):
    healthType: int
    value: float
    value1: Optional[float] = None
