# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED
import os
import re
import sys

from tools.ctrl_executor.cmd_parser import exec_ctrl_cmd
from tools.date_util.market_calendar_cn import MktCalendar
from tools.data.file_hdl import load_text

calendar = MktCalendar()


def load_script(script_path):
    """
    :param script_path: string
    :return:    list of tokens, which is a list of list of strings.
    """
    raw_script = load_text(script_path)
    scripts = []
    for line in raw_script:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                scripts.append(split_line)
    return scripts


if __name__ == '__main__':
    script = load_script(sys.argv[1])
    for l in script:
        model_name = os.path.split(os.path.split(
            os.path.split(sys.argv[1])[0])[0])[1]
        print(">>> %s from %s" % (' '.join(l), model_name))
        exec_ctrl_cmd(model_name, l)
