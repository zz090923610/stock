import os

import re

import sys

from tools.date_util.market_calendar_cn import MktCalendar
from cmd_core.cmd_parser import exec_ctrl_cmd
from tools.file_hdl import load_text

calendar = MktCalendar()


def load_script(script_path):
    raw_script = load_text(script_path)
    script = []
    for line in raw_script:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                script.append(split_line)
    return script


if __name__ == '__main__':
    script = load_script(sys.argv[1])
    for l in script:
        exec_ctrl_cmd(l, calendar)
