#
# (c) Copyright Ascensio System SIA 2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pathlib import Path
from urllib.parse import ParseResult, urlparse, urljoin
import settings


class ConfigurationManager:
    version = '8.0.1'

    def getVersion(self) -> str:
        return self.version

    def document_server_public_url(self) -> ParseResult:
        url = (settings.get_config('onlyOfficeServer'))
        return urlparse(url)

    def document_server_private_url(self) -> ParseResult:
        return self.document_server_public_url()

    def document_server_api_url(self) -> ParseResult:
        server_url = self.document_server_public_url()
        base_url = server_url.geturl()
        path = '/web-apps/apps/api/documents/api.js'
        url = urljoin(base_url, path)
        return urlparse(url)

    def document_server_preloader_url(self) -> ParseResult:
        server_url = self.document_server_public_url()
        base_url = server_url.geturl()
        path = '/web-apps/apps/api/documents/cache-scripts.html'
        url = urljoin(base_url, path)
        return urlparse(url)

    def document_server_command_url(self) -> ParseResult:
        server_url = self.document_server_private_url()
        base_url = server_url.geturl()
        path = '/coauthoring/CommandService.ashx'
        url = urljoin(base_url, path)
        return urlparse(url)

    def document_server_converter_url(self) -> ParseResult:
        server_url = self.document_server_private_url()
        base_url = server_url.geturl()
        path = '/ConvertService.ashx'
        url = urljoin(base_url, path)
        return urlparse(url)

    def jwt_secret(self) -> str:
        return settings.get_config("onlyOfficeSecret")

    def jwt_header(self) -> str:
        return 'Authorization'

    def jwt_use_for_request(self) -> bool:
        return  True

    def ssl_verify_peer_mode_enabled(self) -> bool:
        return  False

    def storage_path(self) -> Path:
        storage_path = settings.get_config("historyVersionPath")
        storage_directory = Path(storage_path)
        if storage_directory.is_absolute():
            return storage_directory
        file = Path(__file__)
        directory = file.parent.joinpath('../..', storage_directory)
        return directory.resolve()

    def languages(self) -> dict[str, str]:
        return {
            'en': 'English',
            'ar': 'Arabic',
            'hy': 'Armenian',
            'az': 'Azerbaijani',
            'eu': 'Basque',
            'be': 'Belarusian',
            'bg': 'Bulgarian',
            'ca': 'Catalan',
            'zh-CN': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)',
            'cs': 'Czech',
            'da': 'Danish',
            'nl': 'Dutch',
            'fi': 'Finnish',
            'fr': 'French',
            'gl': 'Galego',
            'de': 'German',
            'el': 'Greek',
            'hu': 'Hungarian',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'lo': 'Lao',
            'lv': 'Latvian',
            'ms': 'Malay (Malaysia)',
            'no': 'Norwegian',
            'pl': 'Polish',
            'pt': 'Portuguese (Brazil)',
            'pt-PT': 'Portuguese (Portugal)',
            'ro': 'Romanian',
            'ru': 'Russian',
            'sr-Latn-CS': 'Serbian',
            'si': 'Sinhala (Sri Lanka)',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'es': 'Spanish',
            'sv': 'Swedish',
            'tr': 'Turkish',
            'uk': 'Ukrainian',
            'vi': 'Vietnamese',
            'aa-AA': 'Test Language'
        }
