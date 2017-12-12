# Copyright (c) 2017 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui
import os

from pygments import lex
from pygments.lexers import Python3Lexer
from pygments.token import Token

from cui.util import intersperse

# TODO fix escaped linebreaks

token_map = {
    Token.Comment.Hashbang:        {'foreground': 'comment'},
    Token.Comment.Single:          {'foreground': 'comment'},
    Token.Keyword:                 {'foreground': 'keyword'},
    Token.Keyword.Constant:        {'foreground': 'keyword'},
    Token.Keyword.Namespace:       {'foreground': 'keyword'},
    Token.Name.Builtin.Pseudo:     {'foreground': 'keyword'},
    Token.Name.Builtin.Pseudo:     {'foreground': 'keyword'},
    Token.Name.Decorator:          {'foreground': 'py_decorator'},
    Token.Name.Function:           {'foreground': 'function'},
    Token.Name.Function.Magic:     {'foreground': 'function'},
    Token.Literal.String.Double:   {'foreground': 'string'},
    Token.Literal.String.Single:   {'foreground': 'string'},
    Token.Literal.String.Doc:      {'foreground': 'string'},
    Token.Literal.String.Escape:   {'foreground': 'string_escape'},
    Token.Literal.String.Interpol: {'foreground': 'string_interpol'}
}


def read_code(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def get_rows(file_path):
    row = []
    for ttype, tcontent in lex(read_code(file_path), Python3Lexer()):
        # Handle multiline tokens
        splitted_content = intersperse(
            [(Token.Literal.String.Doc, tcontent)
             for tcontent in tcontent.split('\n')] \
            if ttype is Token.Literal.String.Doc else \
            [(ttype, tcontent)],
            (Token.Text, '\n')
        )

        # Yield tokens
        for ttype, tcontent in splitted_content:
            if tcontent in ['\n', '\\\n']:
                yield row
                row = []
            else:
                tstyle = token_map.get(ttype)
                if tstyle:
                    token = tstyle.copy()
                    token['content'] = tcontent
                    row.append(token)
                else:
                    row.append(tcontent)
    yield row


class SourceManager(object):
    def __init__(self):
        self._sources = {}

    def get_file(self, file_path, revert=False):
        if file_path not in self._sources or revert:
            self._sources[file_path] = list(get_rows(file_path))
        return self._sources[file_path]


cui.def_variable(['open-files'], SourceManager())


def open_file(path, revert=False):
    return cui.get_variable(['open-files']).get_file(path, revert)


class BaseFileBuffer(cui.buffers.ListBuffer):
    """
    Base Class for buffers displaying files.

    This buffer supports multiline
    """

    def __init__(self, *args, **kwargs):
        super(BaseFileBuffer, self).__init__(*args, **kwargs)
        self._rows = []

    def set_file(self, file_path):
        self._rows = open_file(file_path)
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


class DirectoryBuffer(cui.buffers.TreeBuffer):
    @classmethod
    def name(cls, path):
        return path

    def __init__(self, path):
        super(DirectoryBuffer, self).__init__(path, show_handles=True)
        self._path = path
        self._roots = []

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


def complete_files(display_completions):
    def _complete_files(completion_id, buffer_content):
        basename = os.path.basename(buffer_content)
        dirname = os.path.dirname(buffer_content)
        matches = list(filter(lambda d: d.startswith(basename), os.listdir(dirname)))
        prefix = os.path.commonprefix(matches)
        result = os.path.join(dirname, prefix)
        if len(matches) == 0:
            cui.message('No completions.')
            return buffer_content
        elif len(matches) == 1:
            if os.path.isdir(result):
                return os.path.join(result, '')
        else:
            display_completions(completion_id,
                                list(map(lambda match: [os.path.join(dirname, ''),
                                                        {'content': match,
                                                         'attributes': ['bold']}],
                                         matches)))
        return result
    return _complete_files


def read_file(prompt, default=None):
    f = default or os.path.join(os.getcwd(), '')
    while True:
        f = cui.read_string(prompt, f, complete_files)
        if os.path.exists(f):
            return f
        cui.message('File \'%s\' does not exist.' % f)


@cui.api_fn
@cui.global_key('C-x C-f')
@cui.interactive(lambda: read_file('Find file'))
def find_file(f):
    cui.switch_buffer(FileBuffer if os.path.isfile(f) else DirectoryBuffer, f)
