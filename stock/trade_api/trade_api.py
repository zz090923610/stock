#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import hashlib
import os
import pickle
import threading

import requests
from urllib.parse import urlencode, quote_plus

import time

import stock.trade_api.trade_vars as vs
from stock.common.daemon_class import DaemonClass

from stock.common.variables import COMMON_VARS_OBJ
import daemon.pidfile


class TradeAPI(DaemonClass):
    def __init__(self, broker='gtja', topic_sub='trade_api_req', topic_pub='trade_api_update'):
        super().__init__(topic_sub=topic_sub, topic_pub=topic_pub)
        if broker == '':
            return None
        self.broker = broker
        self.trade_prefix = '%s%s%s' % (vs.P_TYPE[self.broker],
                                        vs.DOMAINS[self.broker],
                                        vs.ACTION_PORTAL[self.broker])
        self.heart_active = True
        self.s = requests.session()
        self.captcha_db = {}
        self.s.headers.update(vs.AGENT)
        self.msg_on_exit = 'trade_api_exit'
        self.user = ''
        self.passwd = ''
        self.v_code = ''

    def get_captcha(self):
        res_captcha = self.s.get(vs.CAPTCHA[self.broker])
        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open('%s/trade_api/Captcha_%s/%s.jpg' % (COMMON_VARS_OBJ.stock_data_root, self.broker, md5), "wb") as file:
            file.write(res_captcha.content)
        self.unblock_publish('md5_fetched_%s' % md5)
        return md5

    def download_captcha_lib(self):
        while True:
            try:
                self.load_captcha_db()
                res_captcha = self.s.get(vs.CAPTCHA[self.broker])
                md5 = hashlib.md5(res_captcha.content).hexdigest()
                with open('%s/trade_api/Captcha_%s/%s.jpg' % (COMMON_VARS_OBJ.stock_data_root, self.broker, md5),
                          "wb") as file:
                    file.write(res_captcha.content)
                self.add_new_captcha(md5, '')
                time.sleep(1)
                print(len(self.captcha_db))
            except requests.exceptions.ConnectionError:
                time.sleep(20)

    def check_captcha_exist(self, md5):
        self.load_captcha_db()
        if md5 in self.captcha_db.keys():
            return self.captcha_db[md5]
        else:
            return None

    def add_new_captcha(self, md5, code):
        self.load_captcha_db()
        if md5 not in self.captcha_db:
            self.captcha_db[md5] = code
            self.save_captcha_db()


    def login(self):
        md5 = self.get_captcha()
        v_code = input()
        self.v_code = v_code
        self.add_new_captcha(md5, v_code)
        return self._login(self.v_code, self.user, self.passwd)
        # if self._login(utils.get_vcode('csc', res)) is False:
        #    print('请确认账号或密码是否正确 ，或券商服务器是否处于维护中。 ')
        # self.keepalive()

    def _login(self, v_code, user, passwd):
        print(v_code, user, passwd)
        trdpwd = base64.b64encode(bytes(passwd, 'utf8')).decode('utf8')

        post_data = {'method': 'login',
                     'uid': self.passwd,
                     'pwdtype': '',
                     'hardInfo': '',
                     'logintype': 'common',
                     'flowno': '',
                     'usbkeySn': '',
                     'usbkeyData': '',
                     'mac': '',
                     'gtja_dating_login_type': 0,
                     'availHeight': 432,
                     'YYBFW': 10,
                     'BranchCode': '1401',
                     'BranchName': '山西太原并州北路证券营业部',
                     'Page': '',
                     'selectBranchCode': '7001',
                     'countType': 'Z',
                     'inputid': user,
                     'trdpwd': trdpwd,
                     'AppendCode': v_code
                     }

        post_data = urlencode(post_data, quote_via=quote_plus)
        print(post_data)
        get_headers = {'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent'],
                       'Upgrade-Insecure-Requests':'1',
                       'Content-Type':'application/x-www-form-urlencoded',
                       'Connection':'keep-alive',
                       'Cache-Control':'max-age=0',
                       'Accept-Encoding':'gzip, deflate, br',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        login_res = self.s.post('https://trade.gtja.com/webtrade/trade/webTradeAction.do',
                               headers=get_headers, data=post_data)
        return login_res
        # logined = self.s.post()
        # if logined.text.find(u'消息中心') != -1:
        #    return True
        # return False

    def load_captcha_db(self):
        if os.path.exists('%s/db.pickle' % vs.CAPTCHA_DB):
            try:
                with open('%s/db.pickle' % vs.CAPTCHA_DB[self.broker], 'rb') as f:
                    self.captcha_db = pickle.load(f)
            except FileNotFoundError:
                self.captcha_db = {}

    def save_captcha_db(self):
        with open('%s/db.pickle' % vs.CAPTCHA_DB[self.broker], 'wb') as f:
            pickle.dump(self.captcha_db, f, -1)

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if payload == 'captcha_req':
            thread = threading.Thread(target=self.get_captcha)
            thread.start()
            self.unblock_publish('md5_fetching')
        elif payload == 'exit':
            self.publish(self.msg_on_exit)
            self.cancel_daemon = True
        elif payload == 'is_alive':
            self.publish('alive_%d' % os.getpid())


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/trade_api.pid' %
                                                       COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):

        a = TradeAPI(broker='gtja')
        a.daemon_main()
