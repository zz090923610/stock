#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Created on 2016年9月25日
@author: Jimmy Liu
@group : waditu
@contact: jimmysoa@sina.cn
'''
import hashlib
import os
import pickle

import requests

import trade_vars as vs

from stock.common.variables import stock_data_root


class TradeAPI(object):
    def __init__(self, broker=''):
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

    def get_captcha(self):
        res_captcha = self.s.get(vs.CAPTCHA[self.broker])
        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open('%s/trade_api/Captcha_%s/%s.jpg' % (stock_data_root,  self.broker, md5), "wb") as file:
            file.write(res_captcha.content)
        return md5

    def check_captcha_exist(self, md5):
        self.load_captcha_db()
        if md5 in self.captcha_db.keys():
            return self.captcha_db[md5]
        else:
            return None

    def add_new_captcha(self, md5, code):
        self.load_captcha_db()
        self.captcha_db[md5] = code
        self.save_captcha_db()

    def login(self):
        md5 = self.get_captcha()
        v_code = input()
        self.add_new_captcha(md5, v_code)
        self._login(v_code, '', '')
        # if self._login(utils.get_vcode('csc', res)) is False:
        #    print('请确认账号或密码是否正确 ，或券商服务器是否处于维护中。 ')
        #self.keepalive()

    def _login(self, v_code, user, passwd):
        print(v_code, user,passwd)
        # logined = self.s.post()
        # if logined.text.find(u'消息中心') != -1:
        #    return True
        # return False

    def load_captcha_db(self):
        if os.path.exists('%s/db.pickle' % vs.CAPTCHA_DB):
            try:
                with open('%s/db.pickle' % vs.CAPTCHA_DB['gtja'], 'rb') as f:
                    self.captcha_db = pickle.load(f)
            except FileNotFoundError:
                self.captcha_db = {}

    def save_captcha_db(self):
        with open('%s/db.pickle' % vs.CAPTCHA_DB['gtja'], 'wb') as f:
            pickle.dump(self.captcha_db, f, -1)


if __name__ == '__main__':
    pass