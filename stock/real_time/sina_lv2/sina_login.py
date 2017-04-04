import base64
import binascii
import http.cookiejar  # 从前的cookie lib
import json
import os
import re
import urllib
import urllib.error
import urllib.parse
import urllib.request

import requests
import rsa


# 用于模拟登陆新浪微博


# noinspection PyBroadException
class SinaLoginHdl:
    def __init__(self, username, password, cookie_path):
        self.cookie_container = http.cookiejar.CookieJar()
        self.cookie_path = cookie_path
        self.password = password
        self.username = username
        self.s = requests.session()
        self.s.headers.update({'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 "
                                             "(KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"})

    def get_prelogin_args(self):

        """
        该函数用于模拟预登录过程,并获取服务器返回的 nonce , servertime , pub_key 等信息
        """
        json_pattern = re.compile('\((.*)\)')
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&' \
              + self.get_encrypted_name() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)'
        try:
            raw_data = self.s.get(url).text
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except Exception as e:
            print("%s" % e)
            return None

    def get_encrypted_pw(self, data):
        rsa_e = 65537  # 0x10001
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.password)
        key = rsa.PublicKey(int(data['pubkey'], 16), rsa_e)
        pw_encrypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        self.password = ''  # 清空password
        password = binascii.b2a_hex(pw_encrypted)
        return password

    def get_encrypted_name(self):
        username_url_like = urllib.request.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_url_like, encoding='utf-8'))
        return username_encrypted.decode('utf-8')

    def enableCookies(self):
        # 建立一个cookies 容器
        # 将一个cookies容器和一个HTTP的cookie的处理器绑定
        cookie_support = urllib.request.HTTPCookieProcessor(self.cookie_container)
        # 创建一个opener,设置一个handler用于处理http的url打开
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        # 安装opener，此后调用urlopen()时会使用安装过的opener对象
        urllib.request.install_opener(opener)

    def build_post_data(self, raw):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com"
                         "%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf": "1",
            "su": self.get_encrypted_name(),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw),
            "sr": "1280*800",
            "encoding": "UTF-8",
            "prelt": "77",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        return post_data

    def login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.enableCookies()
        data = self.get_prelogin_args()
        post_data = self.build_post_data(data)

        try:
            html = self.s.post(url, data=post_data).text
        except Exception as e:
            print(e)
            return 1

        p = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"userdomain":"(.*?)"')

        # noinspection PyBroadException
        try:
            login_url = p.search(html).group(1)
            page = self.s.get(login_url).text
            login_url = 'http://weibo.com/' + p2.search(page).group(1)
            self.s.get(login_url)
            print("Login success!")
            self.save_cookie()
        except:
            print('Login error!')
            return 0

    def load_cookie(self):
        self.s.cookies.clear()
        if os.path.isfile(self.cookie_path):
            with open(self.cookie_path) as f:
                for line in f.read().splitlines():
                    sp = line.split(',')
                    if len(sp) == 4:
                        self.s.cookies.set(sp[0], sp[1], domain=sp[2], path=sp[3])
                        print(sp[0], sp[1])  # , sp[2], sp[3])

    def save_cookie(self):
        try:
            with open(self.cookie_path, 'w') as f:
                for c in self.s.cookies:
                    f.write('%s,%s,%s,%s\n' % (c.name, c.value, c.domain, c.path))
        except Exception as e:
            print('save cookie error', e)
