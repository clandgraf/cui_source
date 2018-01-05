# Copyright (c) 2017 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import cui
import collections

from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound

from cui.util import intersperse


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


class AnnotationSource(object):
    MARKER = 'X'

    def handles_file(path):
        pass

    def get_annotations(path, first_line, length):
        pass


class _SourceManager(object):
    def __init__(self):
        self._sources = {}
        self._annotation_sources = []

    def get_file(self, file_path, revert=False):
        if file_path not in self._sources or revert:
            self._sources[file_path] = list(get_rows(file_path))
        return self._sources[file_path]

    def add_annotation_source(self, annotation_source):
        self._annotation_sources.append(annotation_source)

    def get_annotation_sources_for_file(self, path):
        return (source
                for source in self._annotation_sources
                if source.handles_file(path))

    def get_annotations(self, path, first_line, length):
        annotation_sources = list(self.get_annotation_sources_for_file(path))
        annotations_dict = collections.OrderedDict()
        for source in annotation_sources:
            for annotation in source.get_annotations(path, first_line, length):
                if annotation not in annotations_dict:
                    annotations_dict[annotation] = [source.MARKER]
                else:
                    annotations_dict[annotation].append(source.MARKER)
        return len(annotation_sources), annotations_dict

cui.def_variable(['open-files'], _SourceManager())


def open_file(path, revert=False):
    return cui.get_variable(['open-files']).get_file(path, revert)


def add_annotation_source(annotation_source):
    cui.get_variable(['open-files']).add_annotation_source(annotation_source)


def get_annotations(path, first_line, length):
    return cui.get_variable(['open-files']).get_annotations(path, first_line, length)
