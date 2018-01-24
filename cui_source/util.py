# Copyright (c) 2017 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os


def mode_line_file_str(path, mode_line_columns=None):
    """
    Render a path filename-first. If space given by mode_line_columns,
    runs out, first truncate path from left, then filename from right
    """
    path_prefix, file_name = os.path.split(path)
    if mode_line_columns:
        columns_for_file = len(file_name) + 2
        if mode_line_columns <= columns_for_file:
            return truncate_right(mode_line_columns, file_name)

        columns_for_path = mode_line_columns - columns_for_file
        if columns_for_path < len(path_prefix):
            path_prefix = truncate_left(columns_for_path, path_prefix)

    return '%s<%s>' % (file_name, path_prefix)
