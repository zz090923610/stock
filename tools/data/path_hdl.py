# -*- coding: utf-8 -*-
import platform
from pathlib import Path
import os
import re

from configs.conf import PROGRAM_DATA_ROOT

HOST_OS = platform.system()


def directory_ensure(target_directory):
    """
    make sure target_directory exists.
    :param target_directory: string
    """
    expanded_path = path_expand(target_directory)
    if os.path.exists(expanded_path):
        return
    else:
        os.makedirs(expanded_path, exist_ok=True)


def directory_exists(target_directory):
    """
    check if target_directory exists, wrapper func of os.path.exists with path_expand.
    :param target_directory:    string
    :return:                    boolean
    """
    expanded_path = path_expand(target_directory)
    if os.path.exists(expanded_path):
        return True
    else:
        return False


def directory_clear_content(target_directory):
    """
    remove all files in target_directory
    :param target_directory:    string
    """
    expanded_path = path_expand(target_directory)
    if not os.path.exists(expanded_path):
        return
    files = os.listdir(expanded_path)
    paths = [os.path.join(expanded_path, i) for i in files]
    for i in paths:
        file_remove(i)


def file_exist(target_file):
    """
    check if target_file exists, wrapper version of os.path.exists with path_expand.
    :param target_file: string
    :return:            boolean
    """
    target_file = path_expand(target_file)
    if os.path.exists(target_file):
        return True
    else:
        return False


def file_remove(target_file):
    """
    remove target_file.
    :param target_file: string
    """
    if os.path.split(target_file)[-1] == "TOUCH_INFO":  # Touch info is a feature currently not implemented.
        return
    os.remove(target_file)


def path_expand(path):
    """
    This function should return a full path no matter what input path is a directory or file.
    Only expand, never check whether it's exist.
    Three cases are considered:
    1, path is already a rooted path on Linux or a path start with C, D, E, F..Z on windows, which can be directed accessed.
    2, Path contain ~, on linux it should be expanded to /home/user, on windows it should be expanded to User's Document
        folder.
    3, If path starts with [a-zA-Z0-9], this kind of path should be assumed to be located in program's root data path.
    *, Other path types are considered undefined. Undefined path can be returned, but should with an error log,
        a expanded path should be expanded to DATA_ROOT/undefined/path to make sure other
        paths are not polluted.
    #TODO this function should be called thousand times during processing a normal daily analysis. current implementation is still too heavy.
    :param path: a user specified path string
    :return: a expanded path string which can be used by other functions.
    """
    path = os.path.expanduser(path)
    if os.path.exists(path):
        return path
    elif path == "DATA_ROOT":
        return PROGRAM_DATA_ROOT
    elif "~" in path[:1]:
        if HOST_OS == "Windows":
            return os.path.join(Path.home(), "Documents", path[1:].strip())
        else:  # should be Linux since I hate MacOS
            return os.path.join(Path.home(), path[1:].strip())
    elif re.search(r"^[a-zA-Z0-9]", path):
        return os.path.join(PROGRAM_DATA_ROOT, path.strip())
    else:  # something happen.
        return os.path.join(PROGRAM_DATA_ROOT, "undefined", path.strip())
