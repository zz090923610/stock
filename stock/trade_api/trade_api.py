#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import hashlib
import os
import pickle
import threading

import requests
from urllib.parse import urlencode, quote_plus
from PIL import Image, ImageTk
import tkinter as tk
import time
import random
import stock.trade_api.trade_vars as vs
from stock.common.daemon_class import DaemonClass

from stock.common.variables import COMMON_VARS_OBJ
import daemon.pidfile
def load_image(path):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=500, height=500)
    canvas.pack()
    img = Image.open(path)
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(250, 250, image=tk_img)
    root.mainloop()

class TradeAPI(DaemonClass):
    def __init__(self, broker='gtja', topic_sub='trade_api_req', topic_pub='trade_api_update'):
        super().__init__(topic_sub=topic_sub, topic_pub=topic_pub)
        if broker == '':
            return None
        self.broker = broker
        self.heart_active = True
        self.captcha_db = {}

        self.msg_on_exit = 'trade_api_exit'
        self.user = ''
        self.passwd = ''
        self.v_code = ''

        self.s = requests.session()
        self.s.headers.update(vs.AGENT)
        self.heart_thread = threading.Thread(target=self.send_heartbeat,
                                             daemon=True)
        self.load_captcha_db()

    def get_captcha(self): # FIXME refresh captcha always failed
        res_captcha = self.s.get('https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp?ran=%f' %
                                 random.uniform(0, 1))
        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open('%s/trade_api/Captcha_%s/%s.jpg' % (COMMON_VARS_OBJ.stock_data_root, self.broker, md5), "wb") as file:
            file.write(res_captcha.content)
        self.unblock_publish('md5_fetched_%s' % md5)


    def download_captcha_lib(self):
        while True:
            try:
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
        if md5 not in self.captcha_db:
            self.captcha_db[md5] = code
            self.save_captcha_db()

    def pre_login(self):
        self.s.headers.update(vs.AGENT)
        self.s.get('https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=preLogin')
        res_captcha = self.s.get('https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp')
        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open('%s/trade_api/Captcha_%s/%s.jpg' % (COMMON_VARS_OBJ.stock_data_root, self.broker, md5), "wb") as file:
            file.write(res_captcha.content)
        self.unblock_publish('md5_fetched_%s' % md5)

    def login(self):
        vcode = self.v_code
        login_status = self._login(vcode)

        if login_status is False:
            print('Login failed')
        else:
            print('Login success')
            self.keepalive()

    def _login(self, v_code):
        trdpwd = base64.b64encode(bytes(self.passwd, 'utf8')).decode('utf8')
        login_params = {'method': 'login',
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
                        'inputid': self.user,
                        'trdpwd': trdpwd,
                        'AppendCode': v_code
                        }
        logined = self.s.post('https://trade.gtja.com/webtrade/trade/webTradeAction.do',
                              data=login_params)
        if logined.text.find(u'国泰君安证券欢迎您') != -1:
            self.unblock_publish('login_success')
            return True
        self.unblock_publish('login_failed')
        return False

    def keepalive(self):
        if self.heart_thread.is_alive():
            self.heart_active = True
        else:
            self.heart_thread.start()

    def send_heartbeat(self):
        while True:
            if self.heart_active:
                try:
                    b = self.s.get('https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=searchStackDetail')
                    if b.text.find('资金帐户状况') == '-1':
                        print('dead')
                        raise LookupError
                    else:
                        print('alive')
                except:
                    self.login()
                time.sleep(100)
            else:
                time.sleep(10)

    def load_captcha_db(self):
        if os.path.exists('%s/db.pickle' % vs.CAPTCHA_DB[self.broker]):
            try:
                with open('%s/db.pickle' % vs.CAPTCHA_DB[self.broker], 'rb') as f:
                    self.captcha_db = pickle.load(f)
            except FileNotFoundError:
                self.captcha_db = {}
        if not os.path.isdir('%s' % vs.CAPTCHA_DB[self.broker]):
            os.makedirs('%s' % vs.CAPTCHA_DB[self.broker])
        file_list = os.listdir('%s' % vs.CAPTCHA_DB[self.broker])
        for f in file_list:
            self.captcha_db[f.split('.')[0]] = ''

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
