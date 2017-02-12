#!/usr/bin/python3

# !/usr/bin/env python
# -*- coding:utf-8 -*-

from common_func import *

def get_parsed_announcement_for_stock(stock, date):
    dlist = BasicInfoHDL.load_announcements_for(stock, date)
    final_str = ''
    for i in dlist:
        final_str += '<a href="%s">%s</a>\n' % (i['adjunctUrl'], i['announcementTitle'])
    return final_str
