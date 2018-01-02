# Copyright (c) 2017 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui
import os

from cui_source import source_manager
from cui_source import api

class BaseFileBuffer(cui.buffers.ListBuffer):
    """
    Base Class for buffers displaying files.

    This buffer supports multiline
    """

    def __init__(self, *args, **kwargs):
        super(BaseFileBuffer, self).__init__(*args, **kwargs)
        self._rows = []

    def set_file(self, file_path):
        self._rows = source_manager.open_file(file_path)
        self.set_variable(['win/buf', 'selected-item'], 0)

    def items(self):
        return self._rows

    def render_item(self, window, item, index):
        return [['%%%dd' % len(str(len(self._rows))) % (index + 1), ' ', item]]


class FileBuffer(BaseFileBuffer):
    """
    Display the source of the file being currently debugged.
    """

    @classmethod
    def name(cls, path):
        return path

    def __init__(self, path):
        super(FileBuffer, self).__init__(path)
        self.set_file(path)
        self.def_variable(['cwd'], os.path.dirname(path))


class DirectoryBuffer(cui.buffers.TreeBuffer):
    @classmethod
    def name(cls, path):
        return path

    def __init__(self, path):
        super(DirectoryBuffer, self).__init__(path, show_handles=True)
        self._path = path
        self._roots = []
        self.def_variable(['cwd'], path)

    def _create_nodes(self, parent, files):
        return list(map(lambda f: {'file': os.path.join(parent, f),
                                   'name': f,
                                   'expanded': False,
                                   'has_children': os.path.isdir(os.path.join(parent, f)),
                                   'children': None},
                        files))

    def get_roots(self):
        if not self._roots:
            self._roots = self._create_nodes(self._path, os.listdir(self._path))
        return self._roots

    def on_item_selected(self):
        item = self.selected_item()
        api.find_file(item['file'])

    def is_expanded(self, item):
        return item['expanded']

    def set_expanded(self, item, expanded):
        item['expanded'] = expanded

    def has_children(self, item):
        return item['has_children']

    def fetch_children(self, item):
        item['children'] = self._create_nodes(item['file'], os.listdir(item['file']))
        if not item['children']:
            item['has_children'] = False

    def get_children(self, item):
        return item['children']

    def render_node(self, window, item, depth, width):
        return [item['name']]