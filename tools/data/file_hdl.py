# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import csv

from tools.data.path_hdl import file_exist
from tools.io import logging


def load_csv(path, col_type=None):
    """
    naive csv file loader.
    :param path: input csv path
    :param col_type: optional dict, specify column data type, like float, int, etc.
    :return: a list of dict. like [{'col1':'row1_col1_val'},{'col1':'row2_col1_val'}]
    """
    if col_type is None:
        col_type = {}
    final_list = []
    try:
        with open(path, encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # noinspection PyTypeChecker
                if len(col_type.keys()) > 0:
                    try:
                        for key in col_type.keys():
                            if col_type[key] == 'float':
                                row[key] = float(row[key])
                            elif col_type[key] == 'int':
                                row[key] = int(float(row[key]))
                        final_list.append(row)
                    except ValueError as e:
                        logging("CSVLoader", "[ ERROR ] Exception when loading %s row:%r : %s" % (path, row, e),
                                method='all')
                else:
                    final_list.append(row)
        return final_list
    except FileNotFoundError:
        return None


def load_text(path):
    """
    naive text file loader
    :param path: input text file path
    :return: a list of string, each string represents a line from text file
    """
    if not file_exist(path):
        logging("TextLoader", "[ ERROR ] file not exist %s" % path)
        return None
    with open(path, encoding='utf8') as f:
        raw_text = f.readlines()
    return raw_text


def save_text(path, content):
    with open(path, "w", encoding='utf8') as f:
        f.write(content)


def load_pickle(path):
    try:
        with open(path, 'rb') as f:
            import pickle
            return pickle.load(f)
    except FileNotFoundError:
        logging("PickleLoader", "[ ERROR ] file not found %s" % path)
        return None


def save_pickle(obj, path):
    try:
        with open(path, 'wb') as f:
            import pickle
            pickle.dump(obj, f, -1)
    except Exception as e:
        logging("PickleSaver", "[ ERROR ] save to %s failed %s" % (path, e))
