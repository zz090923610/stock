# -*- coding: utf-8 -*-
# DEP_APT( zip )

import os

from tools.data.path_hdl import path_expand
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging

calendar = MktCalendar()


# WINDOWS_NOT_GUARANTEED

# CMDEXPORT ( ZIP {output_path} {input_path_list_str[2:]} ) zip_files
def zip_files(output_path, input_path_list_str):
    # currently doesn't support wildcard expand
    input_path_list = input_path_list_str.split(" ")
    input_path_list = [path_expand(calendar.expand_date_in_str(i)) for i in input_path_list]
    cmd = "zip -j %s %s" % (path_expand(calendar.expand_date_in_str(output_path)), " ".join(input_path_list))
    logging("ZIP FILES", "[ INFO ] %s" % cmd, method='all')
    os.system(cmd)
    # Should I take care of cmd result?


# CMDEXPORT ( SEND FILE WECHAT {path} {to} ) send_file_wechat
def send_file_wechat(path, to):
    cmd = "wccmd -f %s %s" % (path_expand(calendar.expand_date_in_str(path)), to)
    logging("SEND FILE WECHAT", "[ INFO ] %s" % cmd, method='all')
    os.system(cmd)
    # Should I take care of cmd result?
