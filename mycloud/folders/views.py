#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import shutil
import traceback
from sqlalchemy.exc import NoResultFound
from mycloud import models
from mycloud.database import FileExplorer
from mycloud.onlyoffice.views import remove
from settings import ROOT_PATH, ENABLE_ONLYOFFICE
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.calc import beauty_size


async def get_disk_usage(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        data = []
        for k, v in ROOT_PATH.items():
            info = shutil.disk_usage(v)
            data.append({'disk': k, 'total': beauty_size(info.total), 'free': beauty_size(info.free),
                         'used': round(info.used / info.total * 100, 2), 'enableOnlyoffice': ENABLE_ONLYOFFICE})
        result.data = data
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_folders_by_id(folder_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(folder_id) == 1:
            folder_id = folder_id + hh.username
        if len(folder_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        folders = FileExplorer.filter_condition(equal_condition={'parent_id': folder_id, 'format': 'folder'}, not_equal_condition={'status': -1}).all()
        folder_list = [models.CatalogGetInfo.model_validate(f) for f in folders if f.id.startswith(tuple('123456789'))]
        folder_path = FileExplorer.get_one(folder_id).full_path
        for k, v in ROOT_PATH.items():
            tmp1 = folder_path.replace('\\', '/')
            tmp2 = v.replace('\\', '/') + '/' + hh.username
            full_path = tmp1.replace(tmp2, '')
            if len(folder_path) != len(full_path):
                folder_path = f"{k}:{full_path}"
                break
        result.data = {'folder': folder_list, 'path': folder_path}
        result.total = len(result.data['folder'])
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def create_folder(parent_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(parent_id) == 1:
            parent_id = parent_id + hh.username
        if len(parent_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        folder = FileExplorer.create(id=str(int(time.time() * 10000)), name=Msg.Folder.get_text(hh.lang), parent_id=parent_id, format='folder', username=hh.username)
        folder_path = FileExplorer.get_one(folder.id).full_path
        if os.path.exists(folder_path):
            FileExplorer.delete(folder)
            raise FileExistsError
        else:
            os.mkdir(folder_path)
        result.data = folder.id
        result.msg = f"{Msg.Create.get_text(hh.lang).format(folder.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder.id, hh.username, hh.ip))
    except FileExistsError:
        result.code = 1
        result.msg = Msg.FileExist.get_text(hh.lang).format(Msg.Folder.get_text(hh.lang))
    except:
        result.code = 1
        result.msg = result.msg = f"{Msg.Create.get_text(hh.lang).format(Msg.Folder.get_text(hh.lang))}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def rename_folder(query: models.FilesBase, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        folder = FileExplorer.get_one(query.id)
        folder_path = folder.full_path
        new_path = os.path.join(os.path.dirname(folder_path), query.name)
        if os.path.exists(new_path):
            raise FileExistsError
        else:
            os.rename(folder_path, new_path)
            FileExplorer.update(folder, name=query.name)
        result.data = query.id
        result.msg = f"{Msg.Rename.get_text(hh.lang).format(query.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder.id, hh.username, hh.ip))
    except FileExistsError:
        result.code = 1
        result.msg = Msg.RenameError.get_text(hh.lang)
    except:
        result.code = 1
        result.msg = f"{Msg.Rename.get_text(hh.lang).format(query.name)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def move_to_folder(query: models.CatalogMoveTo, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(query.parent_id) == 1:
            query.parent_id = query.parent_id + hh.username
        if len(query.parent_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        if len(query.to_id) == 1:
            query.to_id = query.to_id + hh.username
        if len(query.to_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        froms = FileExplorer.get_one(query.parent_id)
        from_path = froms.full_path
        tos = FileExplorer.get_one(query.to_id)
        to_path = tos.full_path
        for folder_id in query.from_ids:
            folder = FileExplorer.get_one(folder_id)
            shutil.move(os.path.join(from_path, folder.name), to_path)
            FileExplorer.update(folder, parent_id=query.to_id)
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_file_path(folder_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        folder = FileExplorer.get_one(folder_id)
        path_id_list = []
        path_name_list = []
        while folder.parent:
            folder = FileExplorer.get(folder.parent_id)
            if folder.name == hh.username:
                path_id_list.append(folder.parent_id)
                path_name_list.append(folder.parent_id + ':')
                break
            else:
                path_name_list.append(folder.name)
                path_id_list.append(folder.id)
        result.data = {'name': '/'.join(path_name_list[::-1]), 'id': '/'.join(path_id_list[::-1])}
        result.msg = f"{Msg.GetFilePath.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder_id, hh.username, hh.ip))
    except NoResultFound:
        result.code = 1
        result.msg = Msg.FileNotExist.get_text(hh.lang).format(folder_id)
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.GetFilePath.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def delete_file(query: models.IsDelete, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query.delete_type == 0:      # 软删除 或者 从回收站还原
            for file_id in query.ids:
                folder = FileExplorer.get_one(file_id)
                FileExplorer.update(folder, status=query.is_delete)
                logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Delete.get_text(hh.lang).format(folder.name) + Msg.Success.get_text(hh.lang), folder.id, hh.username, hh.ip))

        if query.delete_type == 1 or query.delete_type == 2:       # 硬删除，从回收站彻底删除
            if query.file_type == 'folder':
                folders = FileExplorer.filter(FileExplorer.id.in_(query.ids)).all()
                for folder in folders:
                    try:
                        folder_path = folder.full_path
                        shutil.rmtree(folder_path)
                        FileExplorer.delete(folder)
                        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Delete.get_text(hh.lang).format(folder.name) + Msg.Success.get_text(hh.lang), folder.id, hh.username, hh.ip))
                    except FileNotFoundError:
                        logger.error(traceback.format_exc())
                        result.code = 1
                        result.msg = Msg.FileNotExist.get_text(hh.lang).format(folder.name)
                        logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder.id, hh.username, hh.ip))
                        return result
            if query.file_type == 'file':
                files = FileExplorer.filter(FileExplorer.id.in_(query.ids)).all()
                for file in files:
                    try:
                        os.remove(file.full_path)
                        if file.format in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                            remove(file.id, hh)
                    except FileNotFoundError:
                        result.code = 1
                        result.msg = Msg.FileNotExist.get_text(hh.lang).format(file.name)
                        logger.error(Msg.CommonLog1.get_text(hh.lang).format(Msg.FileNotExist.get_text(hh.lang).format(file.name), file.id, hh.username, hh.ip))
                        logger.error(traceback.format_exc())
                    FileExplorer.delete(file)
                    logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Delete.get_text(hh.lang).format(file.name) + Msg.Success.get_text(hh.lang), file.id, hh.username, hh.ip))

        if query.delete_type == 0 and query.is_delete == 0:
            result.msg = f"{Msg.Restore.get_text(hh.lang).format('')}{Msg.Success.get_text(hh.lang)}"
        else:
            result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Success.get_text(hh.lang)}"
    except:
        result.code = 1
        if query.delete_type == 0 and query.is_delete == 0:
            result.msg = f"{Msg.Restore.get_text(hh.lang).format('')}{Msg.Failure.get_text(hh.lang)}"
        else:
            result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result
