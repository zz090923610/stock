import base64
import hashlib
import random

import os

import requests
import time

import trader.conf as conf

from tools.io import logging
import trader.account_info as account


class TradeAPI:
    # DEPENDENCY( pillow )
    def __init__(self):
        self.broker = 'gtja'
        self.s = requests.session()
        self.v_code = None
        self.user = account.user
        self.passwd = account.passwd
        self.JSESSIONID=None

    def set_verification_code(self, v_code):
        self.v_code = v_code

    def pre_login(self):
        self.s.headers.update(conf.AGENT)

        self.s.get('https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=preLogin')
        res_captcha = self.s.get('https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp')

        md5 = hashlib.md5(res_captcha.content).hexdigest()
        with open(os.path.join("/tmp", "%s_%s.jpg" % (self.broker, md5)),
                  "wb") as file:  # FIXME only available for linux
            file.write(res_captcha.content)
            logging("Trader", 'md5_fetched_%s' % md5)
        self.display_captcha(os.path.join("/tmp", "%s_%s.jpg" % (self.broker, md5)))

    def display_captcha(self, file):
        from PIL import Image
        image = Image.open(file)
        image.show()
        self.set_verification_code(input('captcha: '))



    def set_cookies(self):
        cookie_dict = requests.utils.dict_from_cookiejar(self.s.cookies)
        self.JSESSIONID=cookie_dict['JSESSIONID']
        cookie_dict['BranchName'] = '%u5C71%u897F%u592A%u539F%u5EFA%u8BBE%u5357%u8DEF%u8425%u4E1A%u90E8'
        cookie_dict['MyBranchCodeList'] = '1401'
        cookie_dict['countType'] = 'Z'
        self.s.cookies = requests.utils.cookiejar_from_dict(cookie_dict)

    def login(self):

        trdpwd = base64.b64encode(bytes(self.passwd, 'utf8')).decode('utf8')
        self.set_cookies()
        login_params = {'method': 'login',
                        'uid': self.passwd,
                        'pwdtype': '',
                        'hardInfo': '',
                        'logintype': 'common',
                        'flowno': '',
                        'usbkeySn': '',
                        'usbkeyData': '',
                        'mac': '0.0.0.0',
                        'gtja_dating_login_type': 0,
                        'availHeight': 432,
                        'YYBFW': 10,
                        'BranchCode': 1401,
                        'BranchName': '山西太原并州北路证券营业部',
                        'Page': '',
                        'selectBranchCode': 7001,
                        'countType': 'Z',
                        'inputid': self.user,
                        'trdpwd': trdpwd,
                        'AppendCode': self.v_code
                        }
        logined = self.s.post('https://trade.gtja.com/webtrade/trade/webTradeAction.do',
                              data=login_params)
        self.print_alert(logined)
        #
        #if logined.text.find(u'国泰君安证券欢迎您') != -1:
        #    return True
        #return False

    def send_heartbeat(self):
        try:
            b = self.s.get(
                'https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=searchStackDetail')
            if b.text.find('资金帐户状况') == '-1':
                logging('Trader', 'dead')
            else:
                logging('Trader', 'alive')
        except Exception as e:
            logging('Trader', 'dead')


    def get_paper_buy(self):
        url = 'https://trade.gtja.com/webtrade/trade/PaperBuy.jsp'
        res = self.s.get(url)


    def entrust_buy(self, symbol, price, quant):
        current_milli_time = int(round(time.time() ))
        data = {
            'gtja_entrust_sno': current_milli_time,
            'stklevel': 'N',
            'tzdate': 0,
            'market': 1,
            'stkcode': symbol,
            'radiobutton': 'B',
            'price': price,
            'qty': quant
        }
        headers = {'Host': 'trade.gtja.com',
                    'Connection': 'keep-alive',

                    'Origin': 'https://trade.gtja.com',
                    'Upgrade-Insecure-Requests': 1,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': 'https://trade.gtja.com/webtrade/trade/PaperBuy.jsp',
                    'Accept-Encoding':'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
'Cookie': 'MyBranchCodeList=1401; countType=Z; BranchName=%u5C71%u897F%u592A%u539F%u5EFA%u8BBE%u5357%u8DEF%u8425%u4E1A%u90E8;'+ ' JSESSIONID=%s' %self.JSESSIONID}


        print(data)
        print(headers)

        res = self.s.post('https://trade.gtja.com/webtrade/trade/webTradeAction.do?method=entrustBusinessOut',
                          data=data, headers=headers)
        self.print_alert(res)
        return res

    def print_alert(self, res):
        data =res.content.decode('utf8')
        import re
        print(re.search(r'alert\(.*\)', data).group(0))

    def save_res(self, res):
        with open("/tmp/res.html", 'wb') as f:
            f.write(res.content)
