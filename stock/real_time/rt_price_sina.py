#!/usr/bin/python3
import json
import os
import re
import threading
import time

import daemon.pidfile
import requests
from pandas import DataFrame

from stock.common.common_func import *
from stock.common.daemon_class import DaemonClass
from stock.common.time_util import load_last_date
from stock.common.variables import *

TODAY = load_last_date()


def get_pd_from_rt_data_dict_of_stock(rt_data_dict, stock):
    try:
        return DataFrame(rt_data_dict[stock], index=[-0])
    except KeyError:
        return None


def parse_one_line(line):
    try:
        reg_str = r'(var hq_str_[a-z]{2}([0-9]{6})=)'
        m = re.search(reg_str, line)
        to_replace = m.group(0)
        code = m.group(2)
        line = line.replace(to_replace, '%s,' % code)
        spitted_list = line.split(',')
        final_dict = dict(code=spitted_list[0],
                          open=float(spitted_list[2]),
                          close=float(spitted_list[4]),
                          high=float(spitted_list[5]),
                          low=float(spitted_list[6]),
                          volume=int(spitted_list[9]) / 100,
                          money_volume=float(spitted_list[10]) // 10000,
                          bid_1_size=int(spitted_list[11]) / 100,
                          bid_2_size=int(spitted_list[13]) / 100,
                          bid_3_size=int(spitted_list[15]) / 100,
                          bid_4_size=int(spitted_list[17]) / 100,
                          bid_5_size=int(spitted_list[19]) / 100,
                          bid_1_price=float(spitted_list[12]),
                          bid_2_price=float(spitted_list[14]),
                          bid_3_price=float(spitted_list[16]),
                          bid_4_price=float(spitted_list[18]),
                          bid_5_price=float(spitted_list[20]),
                          ask_1_size=int(spitted_list[21]) / 100,
                          ask_2_size=int(spitted_list[23]) / 100,
                          ask_3_size=int(spitted_list[25]) / 100,
                          ask_4_size=int(spitted_list[27]) / 100,
                          ask_5_size=int(spitted_list[29]) / 100,
                          ask_1_price=float(spitted_list[22]),
                          ask_2_price=float(spitted_list[24]),
                          ask_3_price=float(spitted_list[26]),
                          ask_4_price=float(spitted_list[28]),
                          ask_5_price=float(spitted_list[30]),
                          date=spitted_list[31],
                          time=spitted_list[32])
        final_dict['total_ask_size'] = sum([final_dict['ask_%d_size' % d] for d in range(1, 6)])
        final_dict['total_bid_size'] = sum([final_dict['bid_%d_size' % d] for d in range(1, 6)])
        return final_dict
    except IndexError:
        return None
    except AttributeError:
        return None


def print_a_dict(a_dict):
    rows, columns = [int(x) for x in os.popen('stty size', 'r').read().split()]
    print('=' * columns)
    print('%s %s [%s]' % (a_dict['date'], a_dict['time'], a_dict['code']))
    print('Open %.2f high %.2f low %.2f close/now %.2f' % (
        a_dict['open'], a_dict['high'], a_dict['low'], a_dict['close']))
    print('Total bid %d, Total ask %d' % (a_dict['total_bid_size'], a_dict['total_ask_size']))
    print('-' * columns)
    print('%.2f\t%d' % (a_dict['ask_5_price'], a_dict['ask_5_size']))
    print('%.2f\t%d' % (a_dict['ask_4_price'], a_dict['ask_4_size']))
    print('%.2f\t%d' % (a_dict['ask_3_price'], a_dict['ask_3_size']))
    print('%.2f\t%d' % (a_dict['ask_2_price'], a_dict['ask_2_size']))
    print('%.2f\t%d' % (a_dict['ask_1_price'], a_dict['ask_1_size']))
    print('-' * columns)
    print('%.2f\t%d' % (a_dict['bid_1_price'], a_dict['bid_1_size']))
    print('%.2f\t%d' % (a_dict['bid_2_price'], a_dict['bid_2_size']))
    print('%.2f\t%d' % (a_dict['bid_3_price'], a_dict['bid_3_size']))
    print('%.2f\t%d' % (a_dict['bid_4_price'], a_dict['bid_4_size']))
    print('%.2f\t%d' % (a_dict['bid_5_price'], a_dict['bid_5_size']))
    print('=' * columns)


class RTPrice(DaemonClass):
    """
    sub_topic: rtp_req
    res_topic: rtp_update
    Requests: add-stock, rm-stock, exit, clear
    Responds:{'stock':'002263','ask_5_size': 4616.0, 'ask_3_size': 1964.0, 'bid_2_price': 3.69, 'ask_4_size': 2599.86, 
    'volume': 106213.75, 'bid_1_size': 1311.0, 'code': '002263', 'bid_4_size': 2834.0, 'date': '2017-03-28', 
    'high': 3.72, 'bid_5_size': 2090.0, 'ask_5_price': 3.75, 'close': 3.7, 'bid_3_price': 3.68, 'ask_2_size': 6374.0, 
    'ask_3_price': 3.73, 'time': '15:20:03', 'total_ask_size': 18313.36, 'bid_5_price': 3.66, 'bid_4_price': 3.67, 
    'ask_1_size': 2759.5, 'bid_1_price': 3.7, 'ask_2_price': 3.72, 'money_volume': 3936.0, 'bid_2_size': 10598.0, 
    'ask_4_price': 3.74, 'low': 3.69, 'total_bid_size': 24691.0, 'ask_1_price': 3.71, 'open': 3.7, 'bid_3_size': 7858.0}
    """

    def __init__(self):
        super().__init__(topic_sub=['rtp_req'], topic_pub='rtp_update')
        self.s = requests.session()
        self.monitoring_list = []
        self.msg_on_exit = 'rtp_exit'
        self.pid_file_name = 'rtp.pid'

    def start(self):
        threading.Thread(target=self.monitor_main_loop).start()
        self.daemon_main()

    def mqtt_on_message(self, mqttc, obj, msg):

        payload = msg.payload.decode('utf8')
        print(msg.topic, msg.payload)
        if payload.split('_')[0] == 'add-stock':
            self.add_stock(payload.split('_')[1])
        elif payload.split('_')[0] == 'rm-stock':
            self.rm_stock(payload.split('_')[1])
        elif payload == 'is_alive':
            self.publish('alive_%d' % os.getpid())
        elif payload == 'clear':
            self.monitoring_list = []
        elif payload == 'exit':
            self.publish(self.msg_on_exit)
            self.cancel_daemon = True

    def add_stock(self, stock):
        if stock not in self.monitoring_list:
            if stock in BASIC_INFO.symbol_list:
                self.monitoring_list.append(stock)

    def rm_stock(self, stock):
        if stock in self.monitoring_list:
            self.monitoring_list.remove(stock)

    def monitor_main_loop(self):
        print('starting main loop')
        while not self.cancel_daemon:
            try:
                # for stock in self.monitoring_list:
                # self.get_stock_rtp(stock)
                #    time.sleep(.5)  # FIXME temporary workaround
                self.get_stock_rtp_batch()
                time.sleep(.5)
            except IndexError:
                self.unblock_publish('error_index')

    def get_stock_rtp(self, stock):
        tmp_str = '%s%s' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
        req_url = 'http://hq.sinajs.cn/list=' + tmp_str
        get_headers = {'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent']}
        result = self.s.get(req_url, headers=get_headers, verify=False)
        if result.status_code != 200:
            print('Exception %d' % result.status_code)
        tmp_result = result.text
        result = re.sub(r'[\n\"]', '', tmp_result)
        result_line = result.split(";")[0]
        parsed_line = parse_one_line(result_line)
        self.unblock_publish(json.dumps(parsed_line))
        # return parsed_line

    def get_stock_rtp_batch(self):
        stock_list = []
        tmp_str = ''
        monitoring_list = self.monitoring_list.copy()
        for stock in monitoring_list:
            tmp_str += '%s%s,' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
            stock_list.append(tmp_str)
            tmp_str = ''
        tmp_result = ''
        for line in stock_list:
            req_url = 'http://hq.sinajs.cn/list=' + line
            get_headers = {'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent']}
            result = self.s.get(req_url, headers=get_headers, verify=False)
            if result.status_code != 200:
                print('Exception %d' % result.status_code)
            tmp_result += result.text
        result = re.sub(r'[\n\"]', '', tmp_result)
        result_list = result.split(";")
        for line in result_list:
            parsed_line = parse_one_line(line)
            if parsed_line is not None:
                self.unblock_publish(json.dumps(parsed_line))


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/rtp.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):

        a = RTPrice()
        a.start()
