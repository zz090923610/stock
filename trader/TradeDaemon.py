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
        self.proxy = {
            'http': 'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080'
        }
        self.use_proxy = False
        self.heart_thread = threading.Thread(target=self.send_heartbeat,
                                             daemon=True)
        self.load_captcha_db()



    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if payload == 'captcha_req':
            thread = threading.Thread(target=self.get_captcha)
            thread.start()
            self.unblock_publish('md5_fetching')
        elif payload == 'exit':
            self.publish(self.msg_on_exit)
            self.cancel_daemon = True
        elif payload == 'filled_today':
            self.get_filled_today()
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
