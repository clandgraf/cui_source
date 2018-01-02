import cui
import os

from cui_source import buffers


@cui.api_fn
@cui.global_key('C-x C-f')
@cui.interactive(lambda: cui.read_file('Find file'))
def find_file(f):
    """
    Open file ``f`` in a buffer. If ``f`` is a directory,
    ``DirectoryBuffer`` will be used, if it is a file,
    ``FileBuffer`` will be used.

    :param f: The file to be opened.
    """
    cui.switch_buffer(buffers.FileBuffer if os.path.isfile(f) else buffers.DirectoryBuffer, f)
