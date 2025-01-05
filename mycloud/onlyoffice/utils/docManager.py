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


import os
import shutil
import re
import requests
from mycloud.onlyoffice.configuration.configuration import ConfigurationManager
from mycloud.onlyoffice.format.format import FormatManager
from . import fileUtils
import settings


config_manager = ConfigurationManager()
format_manager = FormatManager()


def isCanFillForms(ext):
    return ext in format_manager.fillable_extensions()


# check if the file extension can be viewed
def isCanView(ext):
    return ext in format_manager.viewable_extensions()


# check if the file extension can be edited
def isCanEdit(ext):
    return ext in format_manager.editable_extensions()


# check if the file extension can be converted
def isCanConvert(ext):
    return ext in format_manager.convertible_extensions()


# check if the file extension is supported by the editor (it can be viewed or edited or converted)
def isSupportedExt(ext):
    return isCanView(ext) | isCanEdit(ext) | isCanConvert(ext) | isCanFillForms(ext)


# get internal extension for a given file type
def getInternalExtension(fileType):
    mapping = {
        'word': '.docx',
        'cell': '.xlsx',
        'slide': '.pptx',
        'docxf': '.docxf'
    }
    return mapping.get(fileType, '.docx')  # the default file type is .docx


# get image url for templates
def getTemplateImageUrl(fileType, request_url):
    path = f'{request_url}module/images/'
    mapping = {
        'word': path + 'file_docx.svg',
        'cell': path + 'file_xlsx.svg',
        'slide': path + 'file_pptx.svg'
    }
    return mapping.get(fileType, path + 'file_docx.svg')  # the default file type


# get file name with an index if such a file name already exists
def getCorrectName(filename, file_id: str):
    maxName = 50
    basename = fileUtils.getFileNameWithoutExt(filename)[0:maxName] + ('', '[...]')[len(filename) > maxName]
    ext = fileUtils.getFileExt(filename)
    name = f'{basename}{ext}'

    i = 1
    while os.path.exists(getStoragePath(name, file_id)):  # if file with such a name already exists
        name = f'{basename} ({i}){ext}'  # add an index to its name
        i += 1

    return name


# get server url
def getServerUrl():
    return settings.get_config("onlyOfficeServer")


# get absolute URL to the document storage service
def getCallbackUrl(filename, curAdr):
    host = getServerUrl()
    return f'{host}/onlyoffice/track?filename={filename}&userAddress={curAdr}'


# get url to the created file
def getCreateUrl(host, fileType):
    return f'{host}/onlyoffice/create?fileType={fileType}'


# get url to download a file
def getDownloadUrl(filename):
    host = getServerUrl()
    return f'{host}/download?fileName={filename}'


# get root folder for the current file
def getRootFolder(file_id: str):
    storage_directory = config_manager.storage_path()
    directory = storage_directory.joinpath(file_id)
    if not os.path.exists(directory):  # if such a directory does not exist, make it
        os.makedirs(directory)

    return directory


# get the file history path
def getHistoryPath(file, version, file_id: str):
    directory = getRootFolder(file_id)
    filePath = os.path.join(directory, f'{file_id}-hist', version, file)
    return filePath


# get the file path
def getStoragePath(filename, file_id: str):
    directory = getRootFolder(file_id)
    return os.path.join(directory, fileUtils.getFileName(filename))


# get the path to the forcesaved file version
def getForcesavePath(filename, file_id: str, create):
    storage_directory = config_manager.storage_path()
    directory = storage_directory.joinpath(file_id)
    if not os.path.exists(directory):  # the directory with host address doesn't exist
        return ""

    directory = os.path.join(directory, f'{file_id}-hist')  # get the path to the history of the given file
    if not os.path.exists(directory):
        if create:  # if the history directory doesn't exist
            os.makedirs(directory)  # create history directory if it doesn't exist
        else:  # the history directory doesn't exist and we are not supposed to create it
            return ""

    directory = os.path.join(directory, filename)  # and get the path to the given file
    if not os.path.exists(directory) and not create:
        return ""

    return directory


# save file
def saveFile(response, path):
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


# download file from the given url
def downloadFileFromUri(uri, path=None, withSave=False):
    resp = requests.get(uri, stream=True, verify=config_manager.ssl_verify_peer_mode_enabled(), timeout=5)
    status_code = resp.status_code
    if status_code != 200:  # checking status code
        raise RuntimeError(f'Document editing service returned status: {status_code}')
    if withSave:
        if path is None:
            raise RuntimeError('Path for saving file is null')
        saveFile(resp, path)
    return resp


# remove file from the directory
def removeFile(filename, file_id: str):
    path = getStoragePath(filename, file_id)
    path = os.path.dirname(path)
    if os.path.exists(path):  # remove all the history information about this file
        shutil.rmtree(path)


# generate file key
def generateFileKey(file_path):
    stat = os.stat(file_path)  # get the directory parameters
    h = str(hash(f'{file_path}_{stat.st_mtime_ns}'))
    replaced = re.sub(r'[^0-9-.a-zA-Z_=]', '_', h)
    return replaced[:20]  # take the first 20 characters for the key


# generate the document key value
def generateRevisionId(expectedKey):
    if len(expectedKey) > 20:
        expectedKey = str(hash(expectedKey))

    key = re.sub(r'[^0-9-.a-zA-Z_=]', '_', expectedKey)
    return key[:20]
