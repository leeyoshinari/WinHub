#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import shutil
import zipfile
import traceback
from tortoise import transactions
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist
from mycloud import models
from settings import BASE_PATH
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.calc import calc_md5, calc_file_md5
from common.xmind import read_xmind, create_xmind, generate_xmind8
from common.sheet import read_sheet, create_sheet
from common.md2html import md_to_html


async def create_file(folder_id: str, file_type: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if len(folder_id) == 1:
            folder_id = folder_id + hh.username
        if len(folder_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        folder = await models.Catalog.get(id=folder_id)
        folder_path = await folder.get_all_path()
        async with transactions.in_transaction():
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
            files = await models.Files.create(id=file_id, name=file_name, format=file_type, parent_id=folder_id, size=0, md5='0')
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
            parent_id = parent_id + hh.username
        if len(parent_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        order_type = f'-{query.sort_field}' if query.sort_type == 'desc' else f'{query.sort_field}'
        if parent_id == 'garbage':
            folders = await models.Catalog.filter(is_delete=1).order_by(order_type)
            files = await models.Files.filter(is_delete=1).select_related('parent').order_by(order_type)
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders if f.id.startswith(tuple('123456789')) and f"/{hh.username}" in await f.get_all_path()]
            file_list = [models.FileList.from_orm_format(f).model_dump() for f in files if f"/{hh.username}" in await f.parent.get_all_path()]
        elif parent_id == 'search':
            folders = await models.Catalog.filter(Q(is_delete=0) & Q(name__contains=query.q)).order_by(order_type)
            files = await models.Files.filter(Q(is_delete=0) & Q(name__contains=query.q)).select_related('parent').order_by(order_type)
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders if f.id.startswith(tuple('123456789')) and f"/{hh.username}" in await f.get_all_path()]
            file_list = [models.FileList.from_orm_format(f).model_dump() for f in files if f"/{hh.username}" in await f.parent.get_all_path()]
        else:
            folders = await models.Catalog.filter(Q(parent_id=parent_id) & Q(is_delete=0)).order_by(order_type)
            files = await models.Files.filter(Q(parent_id=parent_id) & Q(is_delete=0)).order_by(order_type)
            folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders if f.id.startswith(tuple('123456789'))]
            file_list = [models.FileList.from_orm_format(f).model_dump() for f in files]
        result.data = folder_list + file_list
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
        async with transactions.in_transaction():
            file = await models.Files.get(id=query.id).select_related('parent')
            folder_path = await file.parent.get_all_path()
            origin_name = file.name
            if len(file_list) > 1:
                file.name = query.name
                file.format = file_list[-1].lower()
            else:
                if file.format:
                    file.name = f"{query.name}.{file.format}"
                else:
                    file.name = query.name
            await file.save()
            if os.path.exists(os.path.join(folder_path, file.name)):
                raise FileExistsError
            else:
                os.rename(os.path.join(folder_path, origin_name), os.path.join(folder_path, file.name))
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
        file = await models.Files.get(id=file_id).select_related('parent')
        parent_path = await file.parent.get_all_path()
        if file.format == 'xmind':
            xmind = read_xmind(os.path.join(parent_path, file.name))
            result.data = xmind
        elif file.format == 'sheet':
            excel = read_sheet(os.path.join(parent_path, file.name))
            result.data = excel
        else:
            try:
                with open(os.path.join(parent_path, file.name), 'r', encoding='utf-8') as f:
                    result.data = f.read()
            except UnicodeDecodeError:
                with open(os.path.join(parent_path, file.name), 'r') as f:
                    result.data = f.read()
        result.msg = file.name
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Query.get_text(hh.lang) + Msg.Success.get_text(hh.lang), file.id, hh.username, hh.ip))
    except KeyError:
        result.code = 1
        result.msg = Msg.FileTypeError.get_text(hh.lang).format(file.format)
        logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    except DoesNotExist:
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
        folder = await models.Files.get(id=file_id)
        path_id_list = []
        path_name_list = []
        while folder.parent:
            folder = await folder.parent.get()
            if folder.name == hh.username:
                path_id_list.append(folder.parent_id)
                path_name_list.append(folder.parent_id + ':')
                break
            else:
                path_name_list.append(folder.name)
                path_id_list.append(folder.id)
        result.data = {'name': '/'.join(path_name_list[::-1]), 'id': '/'.join(path_id_list[::-1])}
        result.msg = f"{Msg.GetFilePath.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except DoesNotExist:
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
        async with transactions.in_transaction():
            file = await models.Files.get(id=query.id).select_related('parent')
            folder_path = await file.parent.get_all_path()
            with open(os.path.join(folder_path, file.name), 'w', encoding='utf-8') as f:
                f.write(query.data)
            file.size = os.path.getsize(os.path.join(folder_path, file.name))
            await file.save()
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
        file = await models.Files.get(id=file_id).select_related('parent')
        folder_path = await file.parent.get_all_path()
        if file.format:
            file_name = f"{file.name.replace(f'.{file.format}', '')} - {Msg.CopyName.get_text(hh.lang)}.{file.format}"
        else:
            file_name = f"{file.name.replace(f'.{file.format}', '')} - {Msg.CopyName.get_text(hh.lang)}"
        async with transactions.in_transaction():
            new_file = await models.Files.create(id=str(int(time.time() * 10000)), name=file_name, format=file.format,
                                                 parent_id=file.parent_id, size=file.size, md5='0')
            if os.path.exists(os.path.join(folder_path, file_name)):
                raise FileExistsError
            shutil.copy2(os.path.join(folder_path, file.name), os.path.join(folder_path, file_name))
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
    file = await models.Files.get(id=file_id).select_related('parent')
    parent_path = await file.parent.get_all_path()
    result = {'path': os.path.join(parent_path, file.name), 'name': file.name, 'format': file.format}
    logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Download.get_text(hh.lang).format(file.name), file.id, hh.username, hh.ip))
    return result


async def zip_file(query: models.DownloadFile, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query.file_type == 'folder':
            files = await models.Files.filter(parent_id=query.ids[0])
            folder = await models.Catalog.get(id=query.ids[0])
            parent_path = await folder.get_all_path()
        else:
            files = await models.Files.filter(id__in=query.ids)
            folder = await models.Catalog.get(id=files[0].parent_id)
            parent_path = await folder.get_all_path()
        zip_path = os.path.join(parent_path, f"{folder.name}.zip")
        if os.path.exists(zip_path):
            result.code = 1
            result.msg = Msg.FileExist.get_text(hh.lang).format(zip_path)
            return result
        zip_multiple_file(zip_path, files, parent_path)
        file = await models.Files.create(id=str(int(time.time() * 10000)), name=f"{folder.name}.zip", format='zip', parent_id=folder.id,
                                         size=os.path.getsize(zip_path), md5=calc_file_md5(zip_path))
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
        file = await models.Files.get(id=query.id).select_related('parent')
        parent_path = await file.parent.get_all_path()
        share = await models.Shares.create(file_id=file.id, name=file.name, path=os.path.join(parent_path, file.name),
                                           format=file.format, times=0, total_times=query.times, username=hh.username)
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
        froms = await models.Catalog.get(id=query.parent_id)
        from_path = await froms.get_all_path()
        tos = await models.Catalog.get(id=query.to_id)
        to_path = await tos.get_all_path()
        for file_id in query.from_ids:
            async with transactions.in_transaction():
                file = await models.Files.get(id=file_id)
                file.parent_id = query.to_id
                await file.save()
                shutil.move(os.path.join(from_path, file.name), to_path)
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Move.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def upload_file_by_path(query: models.ImportLocalFileByPath, hh: models.SessionBase) -> Result:
    try:
        to_folder = await models.Catalog.get(id=query.id)
        to_path = await to_folder.get_all_path()
        for file in os.listdir(query.path):
            file_path = os.path.join(query.path, file)
            if os.path.isfile(file_path):
                md5 = calc_file_md5(file_path)
                try:
                    _ = await models.Files.get(md5=md5)
                    logger.info(f"{Msg.Upload.get_text(hh.lang).format(file)}{Msg.Success.get_text(hh.lang)}")
                    continue
                except DoesNotExist:
                    pass
                try:
                    async with transactions.in_transaction():
                        file_obj = await models.Files.create(id=str(int(time.time() * 10000)), name=file, format=file.split('.')[-1].lower(),
                                                             parent_id=to_folder.id, size=os.path.getsize(file_path), md5=md5)
                        shutil.move(file_path, to_path)
                        logger.info(f"{Msg.Upload.get_text(hh.lang).format(file_obj.name)}{Msg.Success.get_text(hh.lang)}")
                except:
                    logger.error(traceback.format_exc())
                    logger.error(f"{Msg.Upload.get_text(hh.lang).format(file)}{Msg.Failure.get_text(hh.lang)}")
            else:
                async with transactions.in_transaction():
                    folder = await models.Catalog.create(id=str(int(time.time() * 10000)), name=file, parent_id=query.id)
                    folder_path = await folder.get_all_path()
                    os.mkdir(folder_path)
                query1 = models.ImportLocalFileByPath(id=folder.id, path=file_path)
                await upload_file_by_path(query1, hh)
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
        parent_id = parent_id + hh.username
    if len(parent_id) <= 3:
        result.code = 1
        result.data = file_name
        result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
        return result
    data = query['file'].file
    md5 = calc_md5(data)
    try:
        file = await models.Files.get(md5=md5)
        result.code = 2
        result.data = file.name
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file.id, hh.username, hh.ip))
        return result
    except DoesNotExist:
        data.seek(0)
    try:
        folder = await models.Catalog.get(id=parent_id)
        parent_path = await folder.get_all_path()
        file_path = os.path.join(parent_path, file_name)
        file_name_list = file_name.split(".")
        if len(file_name_list) == 1:
            file_type = ''
        else:
            file_type = file_name_list[-1].lower()
        async with transactions.in_transaction():
            file = await models.Files.create(id=str(int(time.time() * 10000)), name=file_name, format=file_type,
                                             parent_id=parent_id, size=query['file'].size, md5=md5)
            with open(file_path, 'wb') as f:
                f.write(data.read())
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
    file = await models.Files.get(id=file_id).select_related('parent')
    parent_path = await file.parent.get_all_path()
    file_path = generate_xmind8(file.id, file.name, os.path.join(parent_path, file.name))
    result = {'path': file_path, 'name': file.name, 'format': file.format}
    logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Export.get_text(hh.lang).format(file.name) + Msg.Success.get_text(hh.lang), file.id, hh.username, hh.ip))
    return result


async def markdown_to_html(file_id: str, hh: models.SessionBase) -> dict:
    result = {'name': '', 'format': '', 'data': ''}
    try:
        file = await models.Files.get(id=file_id).select_related('parent')
        parent_path = await file.parent.get_all_path()
        file_path = os.path.join(parent_path, file.name)
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
        files = await models.Shortcuts.filter(username=hh.username).order_by('id')
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
        file = await models.Files.get(id=file_id)
        _ = await models.Shortcuts.create(file_id=file.id, name=file.name, format=file.format, username=hh.username)
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
        file = await models.Shortcuts.get(id=file_id)
        await file.delete()
        result.msg = f"{Msg.ShortCutsDelete.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except DoesNotExist:
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
        share = await models.Shares.get(id=share_id)
        file = await models.Files.get(id=share.file_id).select_related('parent')
        file_parent_path = await file.parent.get_all_path()
        origin_file_path = os.path.join(file_parent_path, file.name)
        folder = await models.Catalog.get(id=folder_id)
        target_folder_path = await folder.get_all_path()
        async with transactions.in_transaction():
            file = await models.Files.create(id=str(int(time.time() * 10000)), name=file.name, format=file.format, parent_id=folder_id,
                                             size=file.size, md5=file.md5)
            shutil.copy2(origin_file_path, target_folder_path)
        await file.save()
        result.msg = f"{Msg.Save.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Save.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result
