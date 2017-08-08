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
from stock.common.variables import *
from stock_v2.common.communication import simple_publish


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
        final_dict['turnover'] = float(final_dict['volume']) / (
            float(BASIC_INFO.outstanding_dict[final_dict['code']]) * 1000000)
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


class TurnoverMonitor(DaemonClass):
    """
    sub_topic: rtp_update
    res_topic: turnover_update
    Requests: exit
    """

    def __init__(self):
        super().__init__(topic_sub=['rtp_update'], topic_pub='turnover_monitor_update')
        self.s = requests.session()
        self.monitoring_list = []
        self.msg_on_exit = 'turnover_monitor_exit'
        self.pid_file_name = 'turnover_monitor.pid'
        self.turnover_df = DataFrame({'stock': i, 'turnover': 0} for i in BASIC_INFO.symbol_list)

    def start(self):
        msg = 'add-stock_' + ','.join(BASIC_INFO.symbol_list)
        simple_publish('rtp_req', msg)
        threading.Thread(target=self.daemon_main).start()
        self.sorting()

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if payload == 'rtp_exit':
            return
        try:
            data = json.loads(payload)
            #print(msg.topic, msg.payload)
            stock_idx = self.turnover_df[self.turnover_df.stock == data['code']].index.tolist()[0]
            self.turnover_df.loc[stock_idx, 'turnover'] = float(data['turnover'])
        except:
            pass

    def sorting(self):
        while True:
            os.system('clear')
            self.turnover_df= self.turnover_df.sort_values(by='turnover',ascending=False)
            print(self.turnover_df[:60])
            self.turnover_df.to_csv('/tmp/stock/turnover.csv',index=False)
            time.sleep(5)


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/turnover_monitor.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):

        a = TurnoverMonitor()
        a.start()
