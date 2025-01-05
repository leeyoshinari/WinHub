#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: https://github.com/FND/markdown-checklist
import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class ChecklistExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'list_class': ['checklist', 'class name to add to the list element'],
            'render_item': [render_item, 'custom function to render items']
        }
        super(ChecklistExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals=None):
        list_class = self.getConfig('list_class')
        renderer = self.getConfig('render_item')
        postprocessor = ChecklistPostprocessor(list_class, renderer, md)
        md.postprocessors.register(postprocessor, 'checklist', 50)


class ChecklistPostprocessor(Postprocessor):
    """
    adds checklist class to list element
    """
    list_pattern = re.compile(r'(<ul>\n<li>\[[ Xx]\])')
    item_pattern = re.compile(r'^<li>\[([ Xx])\](.*)</li>$', re.MULTILINE)

    def __init__(self, list_class, render_item, *args, **kwargs):
        self.list_class = list_class
        self.render_item = render_item
        super(ChecklistPostprocessor, self).__init__(*args, **kwargs)

    def run(self, html):
        html = re.sub(self.list_pattern, self._convert_list, html)
        return re.sub(self.item_pattern, self._convert_item, html)

    def _convert_list(self, match):
        return match.group(1).replace('<ul>', '<ul class="%s">' % self.list_class)

    def _convert_item(self, match):
        state, caption = match.groups()
        return self.render_item(caption, state != ' ')


def render_item(caption, checked):
    checked = ' checked' if checked else ''
    return '<li><input type="checkbox" disabled%s>%s</li>' % (checked, caption)
