import argparse
import json
import sys
from functools import reduce
from operator import add

from cui_source.source_manager import get_rows


def tostring(line):
    if isinstance(line, list):
        return reduce(add, (tostring(subline) for subline in line), '')
    elif isinstance(line, dict):
        return tostring(line['content'])
    else:
        return line


def dump_raw(f):
    try:
        for line in get_rows(f):
            print(tostring(line))
    except UnicodeDecodeError:
        print("UnicodeDecodeError: %s" % f)


def dump_json(f):
    dump = json.dumps(list(get_rows(f)),
                      indent=4)
    print(dump)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', action='store_true', help='Raw output')
    parser.add_argument('file', help='File to dump')
    args = parser.parse_args()

    (dump_raw if args.raw else dump_json)(args.file)


if __name__ == '__main__':
    main()
