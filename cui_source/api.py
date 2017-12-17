import cui
import os

from cui_source import buffers

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
    """
    Read a file from minibuffer.

    If no ``default`` is provided, the ``cwd`` of the current buffer
    will be used as default. If this yields no value, the systems
    current working directory will be used.

    :param prompt: Prompt to be displayed
    :param default: If provided the default value of
                    the minibuffer is set to this
    """
    f = os.path.join(default or cui.current_buffer(no_minibuffer=True) \
                                   .get_variable(['cwd'], os.getcwd()),
                     '')
    while True:
        f = cui.read_string(prompt, f, complete_files)
        if os.path.exists(f):
            return f
        cui.message('File \'%s\' does not exist.' % f)


@cui.api_fn
@cui.global_key('C-x C-f')
@cui.interactive(lambda: read_file('Find file'))
def find_file(f):
    """
    Open file ``f`` in a buffer. If ``f`` is a directory,
    ``DirectoryBuffer`` will be used, if it is a file,
    ``FileBuffer`` will be used.

    :param f: The file to be opened.
    """
    cui.switch_buffer(buffers.FileBuffer if os.path.isfile(f) else buffers.DirectoryBuffer, f)
