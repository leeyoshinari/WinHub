"""

 (c) Copyright Ascensio System SIA 2024

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

"""

import json
import os
import asyncio
import shutil
import aiofiles
from common.httpRequest import http
from mycloud.onlyoffice.configuration.configuration import ConfigurationManager
from . import jwtManager, docManager, historyManager, fileUtils, serviceConverter


config_manager = ConfigurationManager()


# file saving process
async def processSave(body, filename, file_path, file_id: str):
    # body = resolve_process_save_body(raw_body)
    download = body.get('url')
    if download is None:
        raise Exception("DownloadUrl is null")
    changesUri = body.get('changesurl')
    newFilename = filename
    curExt = fileUtils.getFileExt(filename)  # get current file extension
    downloadExt = "." + body.get('filetype')  # get the extension of the downloaded file

    # convert downloaded file to the file with the current extension if these extensions aren't equal
    if curExt != downloadExt:
        try:
            # convert file and give url to a new file
            convertedData = await serviceConverter.getConvertedData(download, downloadExt, curExt, docManager.generateRevisionId(download), False)
            if not convertedData:
                newFilename = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + downloadExt, file_id)  # get the correct file name if it already exists
            else:
                download = convertedData['uri']
        except Exception:
            newFilename = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + downloadExt, file_id)

    path = await docManager.getStoragePath(file_id, file_id)  # get the file path

    data = await docManager.downloadFileFromUri(download)  # download document file
    if data is None:
        raise Exception("Downloaded document is null")

    histDir = historyManager.getHistoryDir(path)  # get the path to the history direction
    if not await asyncio.to_thread(os.path.exists, histDir):  # if the path doesn't exist
        await asyncio.to_thread(os.makedirs, histDir)  # create it

    versionDir = await historyManager.getNextVersionDir(histDir)  # get the path to the next file version

    # get the path to the previous file version and rename the storage path with it
    await asyncio.to_thread(shutil.copy2, file_path, historyManager.getPrevFilePath(versionDir, curExt))
    await docManager.saveFile(data, file_path)

    if changesUri:
        dataChanges = await docManager.downloadFileFromUri(changesUri)  # download changes file
        if dataChanges is None:
            raise Exception("Downloaded changes is null")
        # save file changes to the diff.zip archive
        await docManager.saveFile(dataChanges, historyManager.getChangesZipPath(versionDir))

    hist = body.get('changeshistory')
    if (not hist) & ('history' in body):
        hist = json.dumps(body.get('history'), ensure_ascii=False)
    if hist:
        # write the history changes to the changes.json file
        await historyManager.writeFile(historyManager.getChangesHistoryPath(versionDir), hist)
    # write the key value to the key.txt file
    await historyManager.writeFile(historyManager.getKeyPath(versionDir), body.get('key'))
    # get the path to the forcesaved file version
    forcesavePath = await docManager.getForcesavePath(newFilename, file_id, False)
    if forcesavePath != "":  # if the forcesaved file version exists
        await asyncio.to_thread(os.remove, forcesavePath)  # remove it


# file force saving process
async def processForceSave(body, filename, file_path, file_id):
    download = body.get('url')
    if download is None:
        raise Exception("DownloadUrl is null")
    curExt = fileUtils.getFileExt(filename)  # get current file extension
    downloadExt = "." + body.get('filetype')  # get the extension of the downloaded file
    newFilename = False
    # convert downloaded file to the file with the current extension if these extensions aren't equal
    if curExt != downloadExt:
        try:
            # convert file and give url to a new file
            convertedData = await serviceConverter.getConvertedData(download, downloadExt, curExt, docManager.generateRevisionId(download), False)
            if not convertedData:
                newFilename = True
            else:
                download = convertedData['uri']
        except Exception:
            newFilename = True

    data = await docManager.downloadFileFromUri(download)  # download document file
    if data is None:
        raise Exception("Downloaded document is null")

    isSubmitForm = body.get('forcesavetype') == 3  # SubmitForm
    if isSubmitForm:
        if newFilename:
            filename = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + "-form" + downloadExt, file_id)  # get the correct file name if it already exists
        else:
            filename = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + "-form" + curExt, file_id)
        forcesavePath = await docManager.getStoragePath(filename, file_id)
    else:
        if newFilename:
            filename = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + downloadExt, file_id)
        forcesavePath = file_path

    await docManager.saveFile(data, forcesavePath)  # save document file

    if isSubmitForm:
        uid = body['actions'][0]['userid']  # get the user id
        await historyManager.createMetaData(filename, uid, "Filling Form", file_id)  # create meta data for forcesaved file

        forms_data_url = body.get('formsdataurl')
        if forms_data_url:
            data_name = await docManager.getCorrectName(fileUtils.getFileNameWithoutExt(filename) + ".txt", file_id)
            data_path = await docManager.getStoragePath(data_name, file_id)
            forms_data = await docManager.downloadFileFromUri(forms_data_url)

            if forms_data is None:
                raise Exception("Document editing service didn't return forms_data")
            else:
                async with aiofiles.open(data_path, 'w') as file:
                    await file.write(forms_data.text)
        else:
            raise Exception('Document editing service did not return forms_data_url')


# create a command request
async def commandRequest(method, key, meta=None):
    payload = {'c': method, 'key': key}
    if meta:
        payload['meta'] = meta

    headers = {'accept': 'application/json'}

    if jwtManager.isEnabled() and jwtManager.useForRequest():  # check if a secret key to generate token exists or not
        headerToken = jwtManager.encode({'payload': payload})  # encode a payload object into a header token
        # add a header Authorization with a header token with Authorization prefix in it
        headers[config_manager.jwt_header()] = f'Bearer {headerToken}'

        payload['token'] = jwtManager.encode(payload)  # encode a payload object into a body token
    response = await http.post(config_manager.document_server_command_url().geturl(), json=payload, headers=headers,
                               ssl=config_manager.ssl_verify_peer_mode_enabled(), timeout=5)

    if meta:
        return response
    return
