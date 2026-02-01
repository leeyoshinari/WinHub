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

import os
import aiofiles
from msgspec.json import decode
from msgspec import Struct
from settings import BASE_PATH


class Format(Struct):
    name: str
    type: str
    actions: list[str]
    convert: list[str]
    mime: list[str]

    def extension(self) -> str:
        return f'.{self.name}'


class FormatManager():
    async def fillable_extensions(self) -> list[str]:
        formats = await self.fillable()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def fillable(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(lambda format: 'fill' in format.actions, formats)
        return list(filtered)

    async def viewable_extensions(self) -> list[str]:
        formats = await self.viewable()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def viewable(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(lambda format: 'view' in format.actions, formats)
        return list(filtered)

    async def editable_extensions(self) -> list[str]:
        formats = await self.editable()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def editable(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(
            lambda format: (
                'edit' in format.actions or
                'lossy-edit' in format.actions
            ),
            formats
        )
        return list(filtered)

    async def convertible_extensions(self) -> list[str]:
        formats = await self.convertible()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def convertible(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(
            lambda format: (
                'auto-convert' in format.actions
            ),
            formats
        )
        return list(filtered)

    async def spreadsheet_extensions(self) -> list[str]:
        formats = await self.spreadsheets()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def spreadsheets(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(lambda format: format.type == 'cell', formats)
        return list(filtered)

    async def presentation_extensions(self) -> list[str]:
        formats = await self.presentations()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def presentations(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(lambda format: format.type == 'slide', formats)
        return list(filtered)

    async def document_extensions(self) -> list[str]:
        formats = await self.documents()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def documents(self) -> list[Format]:
        formats = await self.all()
        filtered = filter(lambda format: format.type == 'word', formats)
        return list(filtered)

    async def all_extensions(self) -> list[str]:
        formats = await self.all()
        mapped = map(lambda format: format.extension(), formats)
        return list(mapped)

    async def all(self) -> list[Format]:
        file_path = os.path.join(BASE_PATH, 'onlyoffice-formats.json')
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            contents = await file.read()
            return decode(contents, type=list[Format])
