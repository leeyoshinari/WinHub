#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import shutil
import zipfile
import traceback
from sqlalchemy import asc, desc
from sqlalchemy.exc import NoResultFound
from mycloud import models
from mycloud.database import FileExplorer, Shortcuts, Shares
from settings import BASE_PATH
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.xmind import read_xmind, create_xmind, generate_xmind8
from common.sheet import read_sheet, create_sheet
from common.md2html import md_to_html


async def create_file(folder_id: str, file_type: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(folder_id) == 1:
            folder_id = folder_id + hh.groupname
        if len(folder_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        folder_path = FileExplorer.get_one(folder_id).full_path
        file_id = str(int(time.time() * 10000))
        if file_type == 'md':
            file_name = Msg.FileMd.get_text(hh.lang)
        elif file_type == 'xmind':
            file_name = Msg.FileXmind.get_text(hh.lang)
        elif file_type == 'sheet':
            file_name = Msg.FileSheet.get_text(hh.lang)
        elif file_type == 'docu':
            file_name = Msg.FileDocu.get_text(hh.lang)
        elif file_type == 'docx':
            file_name = Msg.FileWord.get_text(hh.lang)
        elif file_type == 'xlsx':
            file_name = Msg.FileExcel.get_text(hh.lang)
        elif file_type == 'pptx':
            file_name = Msg.FilePowerPoint.get_text(hh.lang)
        elif file_type == 'py':
            file_name = Msg.FilePy.get_text(hh.lang)
        else:
            file_name = f"{Msg.FileTxt.get_text(hh.lang)}.{file_type}"
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            raise FileExistsError
        else:
            if file_type == 'xmind':
                create_xmind(file_path)
            elif file_type == 'sheet':
                create_sheet(file_path)
            elif file_type in ['docx', 'xlsx', 'pptx']:
                shutil.copy2(f"mycloud/static_files/new.{file_type}", file_path)
            else:
                f = open(file_path, 'w', encoding='utf-8')
                f.close()
        files = FileExplorer.create(id=file_id, name=file_name, format=file_type, parent_id=folder_id, size=0, username=hh.groupname)
        result.data = files.id
        result.msg = f"{Msg.Create.get_text(hh.lang).format(files.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except FileExistsError:
        result.code = 1
        result.msg = Msg.FileExist.get_text(hh.lang).format(file_name)
    except:
        result.code = 1
        result.msg = f"{Msg.Create.get_text(hh.lang).format(file_type)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_all_files(parent_id: str, query: models.SearchItems, hh: models.SessionBase) -> Result:
    """获取目录下的所有文件"""
    result = Result()
    try:
        if len(parent_id) == 1:
            parent_id = parent_id + hh.groupname
        if len(parent_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        order_type = desc(getattr(FileExplorer, query.sort_field)) if query.sort_type == 'desc' else asc(getattr(FileExplorer, query.sort_field))
        not_equal_condition = {'status': -1}
        if parent_id == 'garbage':
            folders = FileExplorer.query(username=hh.groupname, status=-1).order_by(order_type).all()
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders]
        elif parent_id == 'search':
            equal_condition = {'username': hh.groupname}
            like_condition = {'name': query.q}
            folders = FileExplorer.filter_condition(equal_condition=equal_condition, not_equal_condition=not_equal_condition, like_condition=like_condition).order_by(order_type).all()
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders]
        else:
            equal_condition = {'parent_id': parent_id, 'username': hh.groupname}
            folders = FileExplorer.filter_condition(equal_condition=equal_condition, not_equal_condition=not_equal_condition).order_by(order_type).all()
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders]
        result.data = sort_file_list(folder_list)
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, parent_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def rename_file(query: models.FilesBase, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file_list = query.name.split('.')
        file = FileExplorer.get_one(query.id)
        file_path = file.full_path
        folder_path = os.path.dirname(file_path)
        if len(file_list) > 1:
            new_file_name = query.name
            new_file_format = file_list[-1].lower()
        else:
            new_file_format = file.format
            if file.format:
                new_file_name = f"{query.name}.{file.format}"
            else:
                new_file_name = query.name
        new_file_path = os.path.join(folder_path, new_file_name)
        if os.path.exists(new_file_path):
            raise FileExistsError
        else:
            os.rename(file_path, new_file_path)
        FileExplorer.update(file, name=new_file_name, format=new_file_format)
        result.data = query.id
        result.msg = f"{Msg.Rename.get_text(hh.lang).format(file.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
    except FileExistsError:
        result.code = 1
        result.msg = Msg.RenameError.get_text(hh.lang)
    except:
        result.code = 1
        result.msg = f"{Msg.Rename.get_text(hh.lang).format(query.name)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_file_by_id(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(file_id)
        file_path = file.full_path
        if file.format == 'xmind':
            xmind = read_xmind(file_path)
            result.data = xmind
        elif file.format == 'sheet':
            excel = read_sheet(file_path)
            result.data = excel
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result.data = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r') as f:
                    result.data = f.read()
        result.msg = file.name
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Query.get_text(hh.lang) + Msg.Success.get_text(hh.lang), file.id, hh.username, hh.ip))
    except KeyError:
        result.code = 1
        result.msg = Msg.FileTypeError.get_text(hh.lang).format(file.format)
        logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    except NoResultFound:
        result.code = 1
        result.msg = Msg.FileNotExist.get_text(hh.lang).format(file_id)
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_file_path(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(file_id)
        folder = FileExplorer.get_one(file.parent_id)
        folder_ids = folder.full_id
        folder_names = folder.full_path
        disk_no = folder_ids.split('/')[0]
        position = folder_names.index(hh.groupname)
        result.data = {'name': disk_no + ':' + folder_names[position + len(hh.groupname)], 'id': folder_ids}
        result.msg = f"{Msg.GetFilePath.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except NoResultFound:
        result.code = 1
        result.msg = Msg.FileNotExist.get_text(hh.lang).format(file_id)
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.GetFilePath.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def save_txt_file(query: models.SaveFile, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(query.id)
        file_path = file.full_path
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(query.data)
        FileExplorer.update(file, size=os.path.getsize(file_path))
        result.msg = f"{Msg.Save.get_text(hh.lang).format(file.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
    except FileNotFoundError as msg:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = msg.args[0]
    except:
        result.code = 1
        result.msg = f"{Msg.Save.get_text(hh.lang).format(query.id)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def copy_file(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(file_id)
        file_path = file.full_path
        folder_path = os.path.dirname(file_path)
        if file.format:
            file_name = f"{file.name.replace(f'.{file.format}', '')} - {Msg.CopyName.get_text(hh.lang)}.{file.format}"
        else:
            file_name = f"{file.name.replace(f'.{file.format}', '')} - {Msg.CopyName.get_text(hh.lang)}"
        if os.path.exists(os.path.join(folder_path, file_name)):
            raise FileExistsError
        shutil.copy2(file_path, os.path.join(folder_path, file_name))
        new_file = FileExplorer.create(id=str(int(time.time() * 10000)), name=file_name, format=file.format,
                                       parent_id=file.parent_id, size=file.size, username=hh.groupname)
        result.data = new_file.id
        result.msg = f"{Msg.Copy.get_text(hh.lang).format(file.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, new_file.id, hh.username, hh.ip))
    except FileExistsError:
        result.code = 1
        result.msg = Msg.FileExist.get_text(hh.lang).format(file_name)
    except:
        result.code = 1
        result.msg = f"{Msg.Copy.get_text(hh.lang).format(file_id)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def download_file(file_id: str, hh: models.SessionBase) -> dict:
    file = FileExplorer.get_one(file_id)
    result = {'path': file.full_path, 'name': file.name, 'format': file.format}
    logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Download.get_text(hh.lang).format(file.name), file.id, hh.username, hh.ip))
    return result


async def zip_file(query: models.DownloadFile, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query.file_type == 'folder':
            files = FileExplorer.query(parent_id=query.ids[0]).all()
            folder = FileExplorer.get_one(query.ids[0])
            parent_path = folder.full_path
        else:
            files = FileExplorer.filter(FileExplorer.id.in_(query.ids)).all()
            folder = FileExplorer.get_one(files[0].parent_id)
            parent_path = folder.full_path
        zip_path = os.path.join(parent_path, f"{folder.name}.zip")
        if os.path.exists(zip_path):
            result.code = 1
            result.msg = Msg.FileExist.get_text(hh.lang).format(zip_path)
            return result
        zip_multiple_file(zip_path, files, parent_path)
        file = FileExplorer.create(id=str(int(time.time() * 10000)), name=f"{folder.name}.zip", format='zip', parent_id=folder.id,
                                   size=os.path.getsize(zip_path), username=hh.groupname)
        result.data = file.id
        result.msg = f"{Msg.Export.get_text(hh.lang).format(file.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Export.get_text(hh.lang).format(query.ids)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    return result


def zip_multiple_file(zip_path, file_list, parent_path):
    archive = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for file in file_list:
        archive.write(os.path.join(parent_path, file.name), file.name)
    archive.close()


async def share_file(query: models.ShareFile, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(query.id)
        share = Shares.create(file_id=file.id, name=file.name, path=file.full_path,
                              format=file.format, times=0, total_times=query.times, username=hh.groupname)
        result.msg = f"{Msg.Share.get_text(hh.lang).format(share.name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, share.id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Share.get_text(hh.lang).format(query.id)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def move_to_folder(query: models.CatalogMoveTo, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(query.to_id) == 1:
            query.to_id = query.to_id + hh.groupname
        if len(query.to_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        to_path = FileExplorer.get_one(query.to_id).full_path
        for file_id in query.from_ids:
            file = FileExplorer.get_one(file_id)
            if file.parent_id == query.to_id:
                continue
            shutil.move(file.full_path, to_path)
            FileExplorer.update(file, parent_id=query.to_id)
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def upload_file_by_path(query: models.ImportLocalFileByPath, hh: models.SessionBase) -> Result:
    try:
        to_folder = FileExplorer.get_one(query.id)
        to_path = to_folder.full_path
        file_path_list = sorted(os.scandir(query.path), key=lambda x: x.stat().st_mtime)
        for entry in file_path_list:
            file_path = entry.path
            if entry.is_file():
                try:
                    file_size = os.path.getsize(file_path)
                    shutil.move(file_path, to_path)
                    file_obj = FileExplorer.create(id=str(int(time.time() * 10000)), name=entry.name, format=entry.name.split('.')[-1].lower(),
                                                   parent_id=to_folder.id, size=file_size, username=hh.groupname)
                    logger.info(f"{Msg.Upload.get_text(hh.lang).format(file_obj.name)}{Msg.Success.get_text(hh.lang)}")
                except:
                    logger.error(traceback.format_exc())
                    logger.error(f"{Msg.Upload.get_text(hh.lang).format(entry.name)}{Msg.Failure.get_text(hh.lang)}")
            else:
                folder = FileExplorer.create(id=str(int(time.time() * 10000)), name=entry.name, parent_id=query.id, format='ffolder', username=hh.groupname)
                folder_path = folder.full_path
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)
                    query1 = models.ImportLocalFileByPath(id=folder.id, path=file_path)
                    await upload_file_by_path(query1, hh)
                else:
                    FileExplorer.delete(folder)
                    logger.error(f"{Msg.FileExist.get_text(hh.lang).format(folder_path)}")
        logger.info(f"{Msg.Upload.get_text(hh.lang).format(query.path)}{Msg.Success.get_text(hh.lang)}")
        return Result(msg=f"{Msg.Upload.get_text(hh.lang).format(query.path)}{Msg.Success.get_text(hh.lang)}")
    except:
        logger.error(traceback.format_exc())
        return Result(code=1, msg=f"{Msg.Upload.get_text(hh.lang).format(query.path)}{Msg.Failure.get_text(hh.lang)}")


async def upload_file(query, hh: models.SessionBase) -> Result:
    result = Result()
    query = await query.form()
    parent_id = query['parent_id']
    file_name = query['file'].filename
    if len(parent_id) == 1:
        parent_id = parent_id + hh.groupname
    if len(parent_id) <= 3:
        result.code = 1
        result.data = file_name
        result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
        return result
    data = query['file'].file
    # md5 = calc_md5(data)
    # try:
    #     file = await models.Files.get(md5=md5)
    #     result.code = 2
    #     result.data = file.name
    #     result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
    #     logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
    #     return result
    # except DoesNotExist:
    #     data.seek(0)
    try:
        folder = FileExplorer.get_one(parent_id)
        parent_path = folder.full_path
        file_path = os.path.join(parent_path, file_name)
        if os.path.exists(file_path):
            result.code = 1
            result.data = file_name
            result.msg = Msg.FileExist.get_text(hh.lang).format(file_name)
            logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
            return result
        file_name_list = file_name.split(".")
        if len(file_name_list) == 1:
            file_type = ''
        else:
            file_type = file_name_list[-1].lower()
        with open(file_path, 'wb') as f:
            f.write(data.read())
        file = FileExplorer.create(id=str(int(time.time() * 10000)), name=file_name, format=file_type,
                                   parent_id=parent_id, size=os.path.getsize(file_path), username=hh.groupname)
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        result.data = file.name
        logger.info(f"{Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip)}, content_type: {query['file'].content_type}")
    except:
        result.code = 1
        result.data = file_name
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    return result


async def upload_image(query, hh: models.SessionBase) -> Result:
    result = Result()
    query = await query.form()
    img_type = query['imgType']
    folder_path = os.path.join(BASE_PATH, 'web/img/pictures', hh.username)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    if img_type == '1':
        file_path = os.path.join(folder_path, 'background.jpg')
    elif img_type == '0':
        file_path = os.path.join(folder_path, 'avatar.jpg')
    else:
        file_path = os.path.join(folder_path, 'login.jpg')
    data = query['file'].file
    try:
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(query['file'].filename)}{Msg.Success.get_text(hh.lang)}"
        logger.info(f"{Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip)}, content_type: {query['file'].content_type}")
    except:
        result.code = 1
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(query['file'].filename)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    return result


async def export_xmind_file(file_id, hh: models.SessionBase) -> dict:
    file = FileExplorer.get_one(file_id)
    file_path = generate_xmind8(file.id, file.name, file.full_path)
    result = {'path': file_path, 'name': file.name, 'format': file.format}
    logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Export.get_text(hh.lang).format(file.name) + Msg.Success.get_text(hh.lang), file.id, hh.username, hh.ip))
    return result


async def markdown_to_html(file_id: str, hh: models.SessionBase) -> dict:
    result = {'name': '', 'format': '', 'data': ''}
    try:
        file = FileExplorer.get_one(file_id)
        file_path = file.full_path
        with open(file_path, 'r', encoding='utf-8') as f:
            result['data'] = md_to_html(f.read())
        result['name'] = file.name.replace('.md', '.html')
        result['format'] = 'html'
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Export.get_text(hh.lang).format(file.name) + Msg.Success.get_text(hh.lang), file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
    return result


async def get_shortcuts(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        files = Shortcuts.query(username=hh.username).order_by(asc(Shortcuts.id)).all()
        file_list = [models.ShortCutsInfo.model_validate(f).model_dump() for f in files]
        result.data = file_list
        result.total = len(file_list)
        result.msg = f"{Msg.ShortCutsInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.ShortCutsInfo.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def set_shortcuts(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(file_id)
        _ = Shortcuts.create(file_id=file.id, name=file.name, format=file.format, username=hh.username)
        result.msg = f"{Msg.ShortCutsSave.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.ShortCutsSave.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def delete_shortcuts(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = Shortcuts.get_one(file_id)
        Shortcuts.delete(file)
        result.msg = f"{Msg.ShortCutsDelete.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except NoResultFound:
        result.code = 1
        result.msg = Msg.ShortCutsNotExist.get_text(hh.lang)
        logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.ShortCutsDelete.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def save_shared_to_myself(share_id: int, folder_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        share = Shares.get_one(share_id)
        file = FileExplorer.get_one(share.file_id)
        origin_file_path = file.full_path
        folder = FileExplorer.get_one(folder_id)
        target_folder_path = folder.full_path
        shutil.copy2(origin_file_path, target_folder_path)
        file = FileExplorer.create(id=str(int(time.time() * 10000)), name=file.name, format=file.format, parent_id=folder_id,
                                   size=file.size, username=hh.groupname)
        result.msg = f"{Msg.Save.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Save.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


def sort_file_list(file_list: list) -> list:
    if len(file_list) == 0:
        return file_list
    folder_list = [f for f in file_list if f['format'] == 'ffolder']
    f_list = [f for f in file_list if f['format'] != 'ffolder']
    file_type = file_list[0]['format']
    if file_type == 'ffolder':
        return folder_list + f_list
    else:
        return f_list + folder_list
