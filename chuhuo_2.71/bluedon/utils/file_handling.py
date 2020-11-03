#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import os
import json


__author__ = 'ruan.lj@foxmail.com'

def get_lines(path, with_empty_line=True, is_strip=False):
    """get lines for one file readonly
    args:
        path: file path
        with_empty_line: contain empty or not
        is_strip: strip every line or not
    return:
        a generator contain lines of file
    """
    with codecs.open(path, 'r', 'utf8') as fp:
        for line in fp:
            if with_empty_line:
                yield line.strip() if is_strip else line
            elif line.strip():
                yield line.strip() if is_strip else line


def empty_files(*paths):
    """empty files
    args:
        paths: file paths
    return:
        empty files count
    """
    count = 0
    for path in paths:
        if os.path.exists(path):
            open(path, 'w').close()
            count += 1
    return count


def folders_walker(*paths):
    """return all filepath in paths and subfolders
    args:
        paths: folders
    return:
        generator of all filepaths
    """
    for path in paths:
        for root, _, filenames in os.walk(os.path.abspath(path)):
            for filename in filenames:
                yield os.path.join(root, filename)


def newfile_if_no_found(filepath):
    """make file if not found"""
    if not os.path.exists(filepath):
        open(filepath, 'w').close()


def json_load(filepath, default=None):
    """load json from file
    >>> json_load('/tmp/aa', default=333)  #/tmp/aa not exist
    333
    >>> json_dump([1, 2], '/tmp/aaa.json')
    >>> json_load('/tmp/aaa.json')
    [1, 2]
    """

    if not os.path.exists(filepath):
        return default
    try:
        fp = open(filepath, 'r')
        result = json.load(fp)
    except ValueError:
        result = default
    finally:
        fp.close()
    return result


def json_dump(py_obj, filepath):
    """dump jsonable object to file
    >>> json_dump([1, 2], '/tmp/aaa.json')
    >>> json_load('/tmp/aaa.json')
    [1, 2]
    >>> json_dump([1, 2], '/xxx/aaa.json')
    Traceback (most recent call last):
        ...
    ValueError: path '/xxx' do not exist!

    >>> json_dump(set([1, 2]), '/tmp/aaa.json')
    Traceback (most recent call last):
        ...
    TypeError: set([1, 2]) is not JSON serializable

    >>> json_load('/tmp/aaa.json')
    [1, 2]
    """

    base_dir = os.path.split(filepath)[0]
    if not os.path.exists(base_dir):
        raise ValueError("path '%s' do not exist!" % base_dir)
    try:
        fp = open(filepath, 'a+')
        old_data = fp.read()
        fp.seek(0)
        fp.truncate()
        json.dump(py_obj, fp)
    except Exception:
        fp.write(old_data)
        raise
    finally:
        fp.close()
