#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import json


def create_sheet(file_path):
    content = [{"name": "Sheet 1", "status": "1", "order": "0", "row": 66, "column": 26, "celldata": [{"r": 0, "c": 0, "v": {}}], "config": {}, "index": 0}]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False))


def read_sheet(file_path):
    content = json.load(open(file_path, 'r', encoding='utf-8'))
    return content
