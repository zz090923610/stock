# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import csv

from tools.data.path_hdl import file_exist
from tools.io import out


def load_csv(path, col_type=None):
    if col_type is None:
        col_type = {}
    final_list = []
    try:
        with open(path, encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
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
                        # FIXME should be logging
                        print('Loading csv error: %s %s' % (e, '%s %r' % (path, row)))
                else:
                    final_list.append(row)
            for row in reader:
                final_list.append(row)
        return final_list
    except FileNotFoundError:
        return None


def load_text(path):
    if not file_exist(path):
        out("LOADTEXT", "ERROR, file not exist %s" % path)
        return None
    with open(path, encoding='utf8') as f:
        raw_text = f.readlines()
    return raw_text
