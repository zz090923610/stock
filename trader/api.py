import base64
import hashlib
import random

import os

import requests

import trader.conf as conf

from tools.io import logging
import trader.account_info as account


class TradeAPI:
    def __init__(self):
        self.broker = 'gtja'
        self.s = requests.session()
        self.v_code = None
        self.user = account.user
        self.passwd = account.passwd

    def set_verification_code(self, v_code):
        self.v_code = v_code


    def get_captcha(self):  # FIXME refresh captcha always failed
        res_captcha = self.s.get('https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp?ran=%f' %
                                 random.uniform(0, 1))
        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open(os.path.join("/tmp", "%s_%s.jpg" % (self.broker, md5)),
                  "wb") as file:  # FIXME only available for linux
            file.write(res_captcha.content)
        logging("Trader", 'md5_fetched_%s' % md5)

    def pre_login(self):
        self.s.headers.update(conf.AGENT)

        self.s.get('https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=preLogin')
        res_captcha = self.s.get('https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp')

        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open(os.path.join("/tmp", "%s_%s.jpg" % (self.broker, md5)),
                  "wb") as file:  # FIXME only available for linux
            file.write(res_captcha.content)
            logging("Trader", 'md5_fetched_%s' % md5)

    def login(self):
        login_status = self._login(self.v_code)

        if login_status is False:
            logging('Trader', 'Login failed')
        else:
            logging('Trader', 'Login success')

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
            return True
        return False

    def send_heartbeat(self):
        try:
            b = self.s.get(
                'https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=searchStackDetail')
            if b.text.find('资金帐户状况') == '-1':
                logging('Trader', 'dead')
            else:
                logging('Trader','alive')
        except Exception as e:
            logging('Trader', 'dead')
