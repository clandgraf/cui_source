# Copyright (c) 2017 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound

import cui

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
    with open(file_path, 'r', errors='replace') as f:
        return f.read()


def raw_tokens(code, file_path):
    return lex(code, get_lexer_for_filename(file_path, stripnl=False))


def get_tokens(file_path):
    code = read_code(file_path)
    try:
        tokens = raw_tokens(code, file_path)
        for ttype, tcontent in tokens:
        # Split tokens with multiline into sequence of multiple tokens
            yield from intersperse([(ttype, c) for c in tcontent.split('\n')],
                                   (Token.Text, '\n'))
    except ClassNotFound:
        yield from intersperse(((Token.Text, line) for line in code.split('\n')),
                               (Token.Text, '\n'))


def get_rows(file_path):
    row = []
    # Yield tokens
    for ttype, tcontent in filter(lambda token: len(token[1]),
                                  get_tokens(file_path)):
        if tcontent in ['\n', '\\\n']:
            yield row[0] if len(row) == 1 else row
            row = []
        else:
            tstyle = token_map.get(ttype)
            if tstyle:
                token = tstyle.copy()
                token['content'] = tcontent
                row.append(token)
            else:
                row.append(tcontent)
    if len(row):
        yield row


class _SourceManager(object):
    def __init__(self):
        self._sources = {}

    def get_file(self, file_path, revert=False):
        if file_path not in self._sources or revert:
            self._sources[file_path] = list(get_rows(file_path))
        return self._sources[file_path]


cui.def_variable(['open-files'], _SourceManager())


def open_file(path, revert=False):
    return cui.get_variable(['open-files']).get_file(path, revert)
