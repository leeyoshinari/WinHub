#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import json
import time
import shutil
import traceback
from datetime import datetime
from fastapi import Request
from tortoise import transactions
from common.logging import logger
from common.results import Result
from common.messages import Msg
from mycloud import models
from mycloud.database import FileExplorer
from mycloud.onlyoffice.configuration.configuration import ConfigurationManager
from mycloud.onlyoffice.utils import docManager, fileUtils, users, jwtManager, historyManager, trackManager
from settings import PREFIX, TOKENs, ONLYOFFICE_SERVER


onlyoffice_server = ONLYOFFICE_SERVER
server_prefix = PREFIX
config_manager = ConfigurationManager()


async def track(file_id: str, body: str, hh: models.SessionBase):
    response = {}
    try:
        body = json.loads(body)  # read request body
        status = body['status']  # and get status from it

        logger.info(f"{Msg.OnlyOfficeTrack.get_text(hh.lang).format(file_id, status)}")
        if status == 1:  # editing
            if body['actions'] and body['actions'][0]['type'] == 0:  # finished edit
                user = body['actions'][0]['userid']  # the user who finished editing
                if user not in body['users']:
                    # create a command request with the forcasave method
                    trackManager.commandRequest('forcesave', body['key'])

        file = FileExplorer.get_one(file_id)
        file_path = file.full_path

        if (status == 2) | (status == 3):  # mustsave, corrupted
            trackManager.processSave(body, file.name, file_path, file_id)
        if (status == 6) | (status == 7):  # mustforcesave, corruptedforcesave
            trackManager.processForceSave(body, file.name, file_path, file_id)
        FileExplorer.update(file, size=os.path.getsize(file_path))

    except:
        logger.error(traceback.format_exc())
        # set the default error value as 1 (document key is missing or no document with such key could be found)
        response.setdefault("error", 1)

    response.setdefault('error', 0)  # if no exceptions are raised, the default error value is 0 (no errors)
    # the response status is 200 if the changes are saved successfully; otherwise, it is equal to 500
    return json.dumps(response, ensure_ascii=False)


async def edit(file_id: str, request: Request, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        request_url = request.headers.get('referer')
        url_list = request_url.split('/')
        request_host = f"{url_list[0]}//{url_list[2]}"
        file = FileExplorer.get_one(file_id)
        filename = file.name
        ext = fileUtils.getFileExt(filename)
        docKey = docManager.generateFileKey(file.full_path)
        fileType = fileUtils.getFileType(filename)

        # get the editor mode: view/edit/review/comment/fillForms/embedded (the default mode is edit)
        edMode = 'edit' if hh.username else 'view'
        canEdit = docManager.isCanEdit(ext)  # check if the file with this extension can be edited

        if (((not canEdit) and edMode == 'edit') or edMode == 'fillForms') and docManager.isCanFillForms(ext):
            edMode = 'fillForms'
            canEdit = True
        # if the Submit form button is displayed or hidden
        submitForm = edMode == 'fillForms'
        mode = 'edit' if canEdit & (edMode != 'view') else 'view'  # if the file can't be edited, the mode is view

        # types = ['desktop', 'mobile', 'embedded']
        # get the editor type: embedded/mobile/desktop (the default type is desktop)
        edType = 'desktop'

        storagePath = docManager.getStoragePath(file_id, file_id)
        meta = historyManager.getMeta(storagePath)  # get the document meta data

        actionData = ''     # request.GET.get('actionLink')  # get the action data that will be scrolled to (comment or bookmark)
        actionLink = json.loads(actionData) if actionData else None
        createUrl = docManager.getCreateUrl(f"{request_host}{server_prefix}", edType)
        user = users.getUser(hh.username, hh.username)  # get user
        usersInfo = [{"id": user.id, "name": user.name, "email": user.email, "image": '', "group": user.group,
                      "reviewGroups": user.reviewGroups, "commentGroups": user.commentGroups, "favorite": user.favorite,
                      "deniedPermissions": user.deniedPermissions, "descriptions": user.descriptions,
                      "templates": user.templates, "userInfoGroups": user.userInfoGroups, "avatar": user.avatar}]

        if meta:  # if the document meta data exists,
            infObj = {  # write author and creation time parameters to the information object
                'owner': meta['uname'],
                'uploaded': meta['created']
            }
        else:  # otherwise, write current meta information to this object
            infObj = {
                'owner': 'Me',
                'uploaded': datetime.today().strftime('%d.%m.%Y %H:%M:%S')
            }
        infObj['favorite'] = user.favorite
        # specify the document config
        edConfig = {
            'type': edType,
            'documentType': fileType,
            'document': {
                'file_id': file_id,
                'title': filename,
                'url': f"{request_host}{server_prefix}/file/onlyoffice/{file_id}?token={TOKENs[hh.username]}&u={hh.username}&lang={hh.lang}",
                'fileType': ext[1:],
                'key': docKey,
                'lang': hh.lang,
                'info': infObj,
                'permissions': {  # the permission for the document to be edited and downloaded or not
                    'comment': (edMode != 'view') & (edMode != 'fillForms') & (edMode != 'embedded'),
                    'copy': 'copy' not in user.deniedPermissions,
                    'download': 'download' not in user.deniedPermissions,
                    'edit': canEdit & ((edMode == 'edit') | (edMode == 'view') | (edMode == 'filter')),
                    'print': 'print' not in user.deniedPermissions,
                    'fillForms': (edMode != 'view') & (edMode != 'comment') & (edMode != 'embedded'),
                    'modifyFilter': edMode != 'filter',
                    'modifyContentControl': True,
                    'review': canEdit & ((edMode == 'edit') | (edMode == 'review')),
                    'chat': True,
                    'reviewGroups': user.reviewGroups,
                    'commentGroups': user.commentGroups,
                    'userInfoGroups': user.userInfoGroups,
                    'protect': 'protect' not in user.deniedPermissions
                },
                'referenceData': {
                    'instanceId': docManager.getServerUrl(),
                    'fileKey': json.dumps({'fileName': filename, 'userAddress': hh.ip})
                }
            },
            'editorConfig': {
                'actionLink': actionLink,
                'mode': mode,
                'lang': hh.lang,
                'callbackUrl': f"{request_host}{server_prefix}/onlyoffice/track/{file_id}?token={TOKENs[hh.username]}&u={hh.username}&lang={hh.lang}",
                # 'coEditing': {"mode": "strict", "change": False} if edMode == 'view' and user.id == 'uid-0' else None,
                'createUrl': createUrl,
                'templates': [],
                'user': {  # the user currently viewing or editing the document
                    'id': user.id,
                    'name': user.name,
                    'group': user.group,
                    'image': None
                },
                'customization': {  # the parameters for the editor interface
                    'about': True,  # the About section display
                    'comments': True,
                    'feedback': True,  # the Feedback & Support menu button display
                    'forcesave': False,  # adds the request for the forced file saving to the callback handler
                    'submitForm': submitForm,  # if the Submit form button is displayed or not
                    'goback': {  # settings for the Open file location menu button and upper right corner button
                        # the absolute URL to the website address
                        # which will be opened when clicking the Open file location menu button
                        'url': docManager.getServerUrl()
                    }
                }
            }
        }
        # an image which will be inserted into the document
        dataInsertImage = {
            'fileType': 'png',
            'url': f"{request_url}module/onlyoffice/images/logo.png"
        }

        # a document which will be compared with the current document
        dataDocument = {
            'fileType': 'docx',
            'url': f"{request_url}module/onlyoffice/document-templates/new.docx"
        }

        # recipient data for mail merging
        dataSpreadsheet = {
            'fileType': 'csv',
            'url': f"{request_url}module/onlyoffice/document-templates/new.csv"
        }

        # users data for mentions
        usersForMentions = [{'id': user.id, 'name': user.name, 'email': user.email}]
        # users data for protect
        usersForProtect = [{'id': user.id, 'name': user.name, 'email': user.email}]

        if jwtManager.isEnabled():  # if the secret key to generate token exists
            edConfig['token'] = jwtManager.encode(edConfig)  # encode the edConfig object into a token
            dataInsertImage['token'] = jwtManager.encode(dataInsertImage)  # encode the dataInsertImage object into a token
            dataDocument['token'] = jwtManager.encode(dataDocument)  # encode the dataDocument object into a token
            dataSpreadsheet['token'] = jwtManager.encode(dataSpreadsheet)  # encode the dataSpreadsheet object into a token

        result.data = {
            'file_name': filename,
            'cfg': json.dumps(edConfig, ensure_ascii=False),  # the document config in json format
            'fileType': {'word': 'word', 'cell': 'excel', 'slide': 'powerpoint'}[fileType],
            'apiUrl': config_manager.document_server_api_url().geturl(),  # the absolute URL to the api
            # the image which will be inserted into the document
            'dataInsertImage': json.dumps(dataInsertImage, ensure_ascii=False)[1: len(json.dumps(dataInsertImage, ensure_ascii=False)) - 1],
            'dataDocument': json.dumps(dataDocument, ensure_ascii=False),  # document which will be compared with the current document
            'dataSpreadsheet': json.dumps(dataSpreadsheet, ensure_ascii=False),  # recipient data for mail merging
            'usersForMentions': json.dumps(usersForMentions, ensure_ascii=False),
            'usersInfo': json.dumps(usersInfo, ensure_ascii=False),
            'usersForProtect': json.dumps(usersForProtect, ensure_ascii=False),
        }
        logger.info(Msg.OnlyOfficeOpenFile.get_text(hh.lang).format(filename))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
    return result


async def rename(file_id: str, body: str, hh: models.SessionBase):
    response = {}
    try:
        body = json.loads(body)
        newfilename = body['newfilename']
        origExt = '.' + body['ext']
        curExt = fileUtils.getFileExt(newfilename)
        if origExt != curExt:
            newfilename += origExt

        dockey = body['dockey']
        meta = {'title': newfilename}
        async with transactions.in_transaction():
            file = FileExplorer.get_one(file_id)
            file_path = file.full_path
            folder_path = os.path.dirname(file_path)
            if os.path.exists(file_path):
                raise FileExistsError
            else:
                os.rename(file_path, os.path.join(folder_path, newfilename))
                FileExplorer.update(file, name=newfilename, format=body['ext'])
            # trackManager.commandRequest('meta', dockey, meta)
            response.setdefault('result', trackManager.commandRequest('meta', dockey, meta).json())
            logger.info(f"{Msg.Rename.get_text(hh.lang).format(file_id)} {Msg.Success.get_text(hh.lang)}")
    except:
        logger.error(traceback.format_exc())
        response.setdefault("error", 1)
    return json.dumps(response, ensure_ascii=False)


async def save_as(file_id, body: str, hh: models.SessionBase):
    response = {}
    try:
        body = json.loads(body)
        saveAsFileUrl = body['url']
        title = body['title']
        filename = docManager.getCorrectName(title, file_id)
        curExt = fileUtils.getFileExt(filename)
        if not docManager.isSupportedExt(curExt):  # check if the file extension is supported by the document manager
            response.setdefault('error', Msg.FileTypeNotSupport.get_text(hh.lang))
            raise Exception(Msg.FileTypeNotSupport.get_text(hh.lang))

        # save the file from the new url in the storage directory
        file_time = str(int(time.time()))
        path = os.path.join('tmp', file_time)
        if not os.path.exists(path):
            os.makedirs(path)
        docManager.downloadFileFromUri(saveAsFileUrl, os.path.join(path, filename), True)
        response.setdefault('file', filename)
        response.setdefault('file_id', file_time)
        logger.info(f"{Msg.Save.get_text(hh.lang).format(file_id)} {Msg.Success.get_text(hh.lang)}")
    except:
        logger.error(traceback.format_exc())
        response.setdefault('error', 1)

    return json.dumps(response, ensure_ascii=False)


def remove(file_id: str, hh: models.SessionBase):
    try:
        docManager.removeFile(file_id, file_id)
        logger.info(f"{Msg.Delete.get_text(hh.lang).format(file_id)} {Msg.Success.get_text(hh.lang)}")
        return True
    except:
        logger.error(traceback.format_exc())
        return False


async def history_obj(file_id: str, request: Request, body: str, hh: models.SessionBase):
    try:
        url_list = request.headers.get('referer').split('/')
        request_host = f"{url_list[0]}//{url_list[2]}{server_prefix}"
        body = json.loads(body)
        response = {}
        if file_id != body['file_id']:
            response.setdefault('error', Msg.FileNotExist.get_text(hh.lang).format(file_id))
            logger.error(Msg.FileNotExist.get_text(hh.lang).format(file_id))
            return json.dumps(response, ensure_ascii=False)

        file = FileExplorer.get_one(file_id)
        storage_path = docManager.getStoragePath(file_id, file_id)
        doc_key = docManager.generateFileKey(file.full_path)
        file_url = f"{request_host}/file/onlyoffice/{file_id}?token={TOKENs[hh.username]}&u={hh.username}&lang={hh.lang}"
        response = historyManager.getHistoryObject(storage_path, file.name, doc_key, file_url, False, file_id, request_host)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.HistoryRecord.get_text(hh.lang), file_id, hh.username, hh.ip))
        return json.dumps(response, ensure_ascii=False)
    except:
        logger.error(traceback.format_exc())
        return "{\"error\": 1}"


async def download_history(file_id: str, request: Request):
    response = {}
    try:
        file = request.query_params.get('file')
        version = request.query_params.get('ver')
        filePath = docManager.getHistoryPath(file, version, file_id)
        response.setdefault('path', filePath)
    except:
        logger.error(traceback.format_exc())
        response.setdefault('error', 1)
    return response


async def restore(file_id: str, body: str, hh: models.SessionBase):
    try:
        body = json.loads(body)
        file = FileExplorer.get_one(file_id)
        version: int = body['version']
        source_extension = f".{file.format}"
        source_file = file.full_path
        history_directory = historyManager.getHistoryDir(docManager.getStoragePath(file_id, file_id))
        recovery_version_directory = historyManager.getVersionDir(history_directory, version)
        recovery_file = historyManager.getPrevFilePath(recovery_version_directory, source_extension)
        bumped_version_directory = historyManager.getNextVersionDir(history_directory)
        bumped_key = docManager.generateFileKey(source_file)
        bumped_key_file = historyManager.getKeyPath(bumped_version_directory)
        bumped_changes_file = historyManager.getChangesHistoryPath(bumped_version_directory)
        bumped_file = historyManager.getPrevFilePath(bumped_version_directory, source_extension)
        bumped_changes = {
            'serverVersion': config_manager.getVersion(),
            'changes': [{'created': datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'user': {'id': hh.username, 'name': hh.username}}]
        }

        with open(bumped_key_file, 'w', encoding='utf-8') as f:
            f.write(bumped_key)
        with open(bumped_changes_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(bumped_changes, ensure_ascii=False))
        shutil.copy(source_file, bumped_file)
        shutil.copy(recovery_file, source_file)
        FileExplorer.update(file, size=os.path.getsize(source_file))
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.RestoreFromHistory.get_text(hh.lang), file_id, hh.username, hh.ip))
        return "{}"
    except:
        logger.error(traceback.format_exc())
        return "{\"error\": 1}"
