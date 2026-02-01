#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import json
import aiofiles


async def create_sheet(file_path):
    content = [{"name": "Sheet 1", "status": "1", "order": "0", "row": 66, "column": 26, "celldata": [{"r": 0, "c": 0, "v": {}}], "config": {}, "index": 0}]
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(content, ensure_ascii=False))


async def read_sheet(file_path):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        content_str = await f.read()
    content = json.loads(content_str)
    return content
