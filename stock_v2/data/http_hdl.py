import requests

from stock_v2.common.cfg_hdl import *
from bs4 import BeautifulSoup
import pandas as pd


def get_cninfo_mkt(stock):
    """
# if (sc == "shmb" | | sc == "szcn" | | sc == "szsme" | | sc == "szmb"){
#    var market;
#    var mk=stock.substring(0, 1);
#    if (mk == '6'){
#    market="shmb";
#    }else if (mk == '3'){
#    market="szcn";
#    }else if (stock.substring(0, 3) == '002' | | stock.substring(0, 3) == '003' | | stock.substring(0, 3) == '004'){
#    market="szsme";
#    }else{
#    market="szmb";
#    }

    :param stock:
    :return:
    """
    if len(stock) != 6:
        return ''
    if stock[0] == '6':
        return 'shmb'
    elif stock[0] == '3':
        return 'szcn'
    elif (stock[:2] == '00') & (stock[2] in ['2', '3', '4']):
        return 'szsme'
    else:
        return 'szmb'


def converter_to_date(target):
    res = '%s-%s-%s' % (target[:4], target[4:6], target[6:8])
    return res if len(res) == 10 else None


def converter_split_dividend(target):
    try:
        split = re.search(r"转增([0-9]+)", target).group(1)
    except AttributeError:
        split = '0'
    try:
        dividend = re.search(r"派([.0-9]+)", target).group(1)
    except AttributeError:
        dividend = '0'
    return '%s/%s' % (split, dividend)


class HttpHdl:
    def __init__(self, path, param_dict):
        self.path = path
        self.param_dict = param_dict
        self.scripts = load_cfg(path)
        self.s = requests.session()
        self.url = ''
        self.method = ''
        self.status_matched = False
        self.status_required = None
        self.header_dict = {}
        self.decode = None
        self.to_variable = None

    def apply(self):
        for idx, line in enumerate(self.scripts):
            action = line[0]
            if action == 'INPUT':
                for variable in line[1:]:
                    try:
                        todo = """%s = '%s'""" % (variable, self.param_dict[variable])
                        exec(todo)
                    except KeyError:
                        # TODO MQTT LOG
                        pass
            elif action == 'EXEC':
                todo = ' '.join(line[1:])
                exec(todo)
            elif action == 'URL':
                if line[1] == 'EXEC':
                    self.url = eval(line[2])
                else:
                    self.url = line[2]
            elif action == 'METHOD':
                self.method = line[1]
            elif action == 'STATUS':
                self.status_required = line[1]
            elif action == 'DECODE':
                self.decode = line[1]
            elif action == 'TO':
                self.to_variable = line[1]
            elif action == 'HEADER':
                key, val = ' '.join(line[1:]).split(':', 1)
                self.header_dict[key] = val
            elif action == 'DECODE':
                self.decode = line[1]
            elif action == 'APPLY':
                if self.method.upper() == 'GET':
                    self.s.headers = self.header_dict
                    session_get = '%s=self.s.get(self.url, verify=False, timeout=5)' % self.to_variable
                    exec(session_get)
                    status_check = 'self.status_matched=True if %s.status_code == int(self.status_required) else False'\
                                   % self.to_variable
                    exec(status_check)
                    decode = """%s = %s.content.decode('%s')""" % (self.to_variable, self.to_variable, self.decode)
                    exec(decode)

                elif self.method.upper() == 'POST':
                    pass
                    # TODO
            elif action == 'RETURN':
                # FIXME
                self.s.close()
                pass
                # exec('return %s' % ','.join(line[1:]))
