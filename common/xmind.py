#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import time
import json
import random
import codecs
import zipfile
from zipfile import ZipFile
from common import xmltodict


x_manifest = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" password-hint=""><file-entry full-path="content.xml" media-type="text/xml"/><file-entry full-path="META-INF/" media-type=""/><file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/><file-entry full-path="meta.xml" media-type="text/xml"/><file-entry full-path="styles.xml" media-type="text/xml"/><file-entry full-path="Thumbnails/" media-type=""/><file-entry full-path="Thumbnails/thumbnail.png" media-type="image/png"/></manifest>'
x_meta = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"><Author><Name></Name><Email/><Org/></Author><Create><Time>{}</Time></Create><Creator><Name>XMind</Name><Version>R3.7.9.201912052356</Version></Creator><Thumbnail><Origin><X>86</X><Y>141</Y></Origin><BackgroundColor>#FFFFFF</BackgroundColor></Thumbnail></meta>'
x_style = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" version="2.0"><styles>{}</styles></xmap-styles>'
x_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><xmap-content xmlns="urn:xmind:xmap: xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink" modified-by="" timestamp="{}" version="2.0"><sheet id="06hlfldmnedbkgh3r9nsjsrjt1" modified-by="" theme="0u70s3gi0t57b7d6cpqnddcb8k" timestamp="{}"><title>画布 1</title>{}<sheet-settings><info-items><info-item mode="card" type="org.xmind.ui.infoItem.notes"/></info-items></sheet-settings></sheet></xmap-content>'
x_extensions = '<extensions><extension provider="org.xmind.ui.map.unbalanced"><content><right-number>{}</right-number></content></extension></extensions>'
progress = ['', 'start', 'oct', 'quarter', '3oct', 'half', '5oct', '3quar', '7oct', 'done']


def create_xmind(file_path):
    content = {"template": "right", "theme": "fresh-blue", "version": "0", "root": {"data": {"id": str(int(time.time()*1000)), "text": "中心主题"}, "children": [{"data": {"id": str(int(time.time())), "text": "分支主题"}, "children": []}]}}
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False))


def read_xmind(file_path):
    try:
        with ZipFile(file_path, 'r') as z:
            if 'content.json' in z.namelist():
                result = format_zen_reader(json.loads(z.open('content.json').read().decode('utf-8')))
            elif 'content.xml' in z.namelist():
                result = format_x_reader(xmltodict.parse(z.open('content.xml').read().decode('utf-8')))
            else:
                result = None
    except zipfile.BadZipfile:
        result = None
    if result:
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False))
    result = json.load(open(file_path, 'r', encoding='utf-8'))
    return result


def write_xmind(file_path, data):
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)


def generate_xmind8(file_id, file_name, file_path):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    tmp_path = os.path.join('tmp', file_id)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    with open(os.path.join(tmp_path, 'styles.xml'), 'w', encoding='utf-8') as f:
        f.write('')
    content = json.load(open(file_path, 'r', encoding='utf-8'))
    content = format_x_writer(content, os.path.join(tmp_path, 'styles.xml'))
    with open(os.path.join(tmp_path, 'styles.xml'), 'r', encoding='utf-8') as f:
        styles = f.read()
    with codecs.open(os.path.join(tmp_path, 'styles.xml'), 'w', encoding='utf-8') as f:
        f.write(x_style.format(styles))
    with codecs.open(os.path.join(tmp_path, 'content.xml'), 'w', encoding='utf-8') as f:
        f.write(x_content.format(int(time.time()*1000), int(time.time()*1000), content))
    with codecs.open(os.path.join(tmp_path, 'manifest.xml'), 'w', encoding='utf-8') as f:
        f.write(x_manifest)
    with codecs.open(os.path.join(tmp_path, 'meta.xml'), 'w', encoding='utf-8') as f:
        f.write(x_meta.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    new_path = os.path.join(tmp_path, file_name)
    file_names = os.listdir(tmp_path)
    with ZipFile(new_path, "w") as z:
        for file in file_names:
            if 'xmind' in file or 'json' in file: continue
            if 'manifest.xml' == file:
                z.write(os.path.join(tmp_path, file), 'META-INF/' + file)
            else:
                z.write(os.path.join(tmp_path, file), file)
    return new_path


def format_x_reader(data):
    mind = {"template": "right", "theme": "fresh-blue", "version": "0", "root": {}}
    res = {'data': {}, 'children': []}
    for k, v in data['xmap-content']['sheet']['topic'].items():
        if k == 'id':
            res['data'].update({'id': v})
        if k == 'title':
            res['data'].update({'text': v})
        if k == 'structure-class':
            if v == 'org.xmind.ui.map.unbalanced':
                mind['template'] = 'default'
            elif v == 'org.xmind.ui.org-chart.down':
                mind['template'] = 'structure'
            else:
                mind['template'] = 'right'
        if k == 'children':
            res.update({'children': x_reader_children(v['topics']['topic'])})
    mind['root'] = res
    return mind


def format_zen_reader(data: list):
    mind = {"template": "right", "theme": "fresh-blue", "version": "0", "root": {}}
    res = {'data': {}, 'children': []}
    for k, v in data[0]['rootTopic'].items():
        if k == 'id':
            res['data'].update({'id': v})
        if k == 'title':
            res['data'].update({'text': v})
        if k in ['background', 'color', 'font-size', 'font-weight', 'font-style']:
            res['data'].update({k: v})
        if k == 'children':
            res.update({'children': zen_reader_children(v['attached'])})
    mind['root'] = res
    return mind


def zen_reader_children(data: list):
    result = []
    for item in data:
        res = {'data': {}, 'children': []}
        for k, v in item.items():
            if k == 'id':
                res['data'].update({'id': v})
            if k == 'title':
                res['data'].update({'text': v})
            if k in ['background', 'color', 'font-size', 'font-weight', 'font-style']:
                res['data'].update({k: v})
            if k == 'children':
                res.update({'children': zen_reader_children(v['attached'])})
        result.append(res)
    return result


def x_reader_children(data):
    result = []
    if isinstance(data, list):
        for item in data:
            res = {'data': {}, 'children': []}
            for k, v in item.items():
                if k == 'id':
                    res['data'].update({'id': v})
                if k == 'title':
                    if isinstance(v, str):
                        res['data'].update({'text': v})
                    elif isinstance(v, dict):
                        if 'text' in v:
                            res['data'].update({'text': v['text']})
                        else:
                            res['data'].update({'text': None})
                    else:
                        res['data'].update({'text': str(v)})
                if k == 'children' and 'topics' in v and 'topic' in v['topics']:
                    res.update({'children': x_reader_children(v['topics']['topic'])})
            result.append(res)
    else:
        res = {'data': {}, 'children': []}
        for k, v in data.items():
            if k == 'id':
                res['data'].update({'id': v})
            if k == 'title':
                if isinstance(v, str):
                    res['data'].update({'text': v})
                elif isinstance(v, dict):
                    if 'text' in v:
                        res['data'].update({'text': v['text']})
                    else:
                        res['data'].update({'text': None})
                else:
                    res['data'].update({'text': str(v)})
            if k == 'children' and 'topics' in v and 'topic' in v['topics']:
                res.update({'children': x_reader_children(v['topics']['topic'])})
        result.append(res)
    return result


def format_x_writer(data, style_path):
    template = data['template']
    node_num = len(data['root'].get("children", []))
    if template == 'default':
        my_extension = x_extensions.format(int((node_num + 1) / 2))
    else:
        my_extension = ''
    if template == 'default':
        my_structure = 'map.unbalanced'
    elif template == 'structure':
        my_structure = 'org-chart.down'
    else:
        my_structure = 'logic.right'
    style_id = 's' + str(int(time.time() * 1000)) + str(random.randint(1, 99999))
    ss = format_x_styles(style_id, data['root']["data"])
    style_property = ''
    if len(ss) > 5:
        with open(style_path, 'a', encoding='utf-8') as f:
            f.write(ss)
        style_property = f' style-id="{style_id}"'
    topic = f'<topic id="{data["root"]["data"]["id"]}" structure-class="org.xmind.ui.{my_structure}" timestamp="{int(time.time() * 1000)}"{style_property}><title>{deal_xmind_title(data["root"]["data"]["text"])}</title>{format_x_marker(data["root"]["data"])}{format_x_note(data["root"]["data"])}<children><topics type="attached">{format_x_children(data["root"].get("children", []), style_path)}</topics></children>{my_extension}</topic>'
    return topic


def format_x_children(data: list, style_path: str):
    res = ''
    for item in data:
        style_id = 's' + str(int(time.time() * 1000)) + str(random.randint(1, 99999))
        ss = format_x_styles(style_id, item["data"])
        style_property = ''
        if len(ss) > 5:
            with open(style_path, 'a', encoding='utf-8') as f:
                f.write(ss)
            style_property = f' style-id="{style_id}"'
        res += f'<topic id="{item["data"]["id"]}" timestamp="{int(time.time() * 1000)}"{style_property}><title>{deal_xmind_title(item["data"]["text"])}</title>{format_x_marker(item["data"])}{format_x_note(item["data"])}<children><topics type="attached">{format_x_children(item.get("children", []), style_path)}</topics></children></topic>'
    return res


def deal_xmind_title(text: str) -> str:
    if '<' in text:
        text = text.replace('<', '&lt;')
    if '>' in text:
        text = text.replace('>', '&gt;')
    if '&' in text:
        text = text.replace('&', '&amp;')
    return text


def format_x_styles(id: str, data: dict):
    res = '<topic-properties'
    if 'background' in data:
        res += ' svg:fill="{}"'.format(data['background'])
    if 'font-size' in data:
        res += ' fo:font-size="{}pt"'.format(data['font-size'])
    if 'color' in data:
        res += ' fo:color="{}"'.format(data['color'])
    if 'font-weight' in data:
        res += ' fo:font-weight="{}"'.format(data['font-weight'])
    if 'font-style' in data:
        res += ' fo:font-style="{}"'.format(data['font-style'])
    if 'font-family' in data:
        res += ' fo:font-family="{}"'.format(data['font-family'])
    if len(res) > 20:
        res = '<style id="{}" name="" type="topic">{}/></style>'.format(id, res)
        return res
    else:
        return ''


def format_x_marker(data: dict):
    res = ''
    if 'priority' in data and data['priority']:
        res += '<marker-ref marker-id="priority-{}"/>'.format(data['priority'])
    if 'progress' in data and data['progress']:
        res += '<marker-ref marker-id="task-{}"/>'.format(progress[data['progress']])
    if len(res) > 5:
        res = '<marker-refs>{}</marker-refs>'.format(res)
        return res
    else:
        return ''


def format_x_note(data: dict):
    res = ''
    if 'note' in data and data['note']:
        notes = data['note'].split('\n')
        for note in notes:
            res += f'<xhtml:p>{note}</xhtml:p>'
    if len(res) > 5:
        res = f'<notes><plain>{data["note"]}</plain><html>{res}</html></notes>'
        return res
    else:
        return ''

