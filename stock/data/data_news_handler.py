#!/usr/bin/python3
import pickle
import re
import subprocess
import sys

import requests
import resource
from bs4 import BeautifulSoup

from stock.common.common_func import get_today, generate_html
from stock.common.variables import stock_data_root

max_rec = 0x100000
resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
sys.setrecursionlimit(max_rec)


def write_text_file(file, content):
    with open(file, 'wb') as f:
        f.write(content.encode('utf8'))


class NEWS_SRC:
    def __init__(self):
        self.today = get_today()
        self.s = requests.session()
        self.all_data = {}
        self.load()

    def _get_src_news_of_day(self, day):
        print("Fetching SRC news %s" % day)
        req_url = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd/index.html'
        result = self.s.get(req_url, verify=False)
        b = result.content.decode('utf-8')
        soup = BeautifulSoup(b, 'lxml')

        c = soup.find("div", {"id": "documentContainer"})
        d = c.findAll('li')
        parsed_list = []
        for item in d:
            ori_link = item.find('a')['href']
            link = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd' + \
                   re.search(r"^.(/[a-zA-Z0-9/._]+)", ori_link).group(1)
            title = item.find('a')['title']
            date = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(item.find('span'))).group(1)
            if date == day:
                parsed_list.append({'link': link, 'title': title, 'date': date})
        return parsed_list

    def _get_src_announcement_of_day(self, day):
        print("Fetching SRC announcement %s" % day)
        req_url = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwfbh/'
        result = self.s.get(req_url, verify=False)
        b = result.content.decode('utf-8')
        soup = BeautifulSoup(b, 'lxml')

        c = soup.find("div", {"id": "documentContainer"})
        d = c.findAll('li')
        parsed_list = []
        for item in d:
            ori_link = item.find('a')['href']
            link = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd' + \
                   re.search(r"^.(/[a-zA-Z0-9/._]+)", ori_link).group(1)
            title = item.find('a')['title']
            date = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(item.find('span'))).group(1)
            if date == day:
                parsed_list.append({'link': link, 'title': title, 'date': date})
        return parsed_list

    def fetch_all_of_day(self, day):
        try:
            _ = self.all_data[day]
        except KeyError:
            news = self._get_src_news_of_day(day)
            announcement = self._get_src_announcement_of_day(day)
            self.all_data[day] = {'news': news, 'announcement': announcement}
            with open('%s/news/zjh/zjh.pickle' % stock_data_root, 'wb') as f:
                pickle.dump(self.all_data, f, -1)

    def load(self):
        try:
            with open('%s/news/zjh/zjh.pickle' % stock_data_root, 'rb') as f:
                self.all_data = pickle.load(f)
        except FileNotFoundError:
            return {}
        except EOFError:
            return {}

    def generate_html_of_day(self, day):
        news = self.all_data[day]['news']
        announcement = self.all_data[day]['announcement']
        html_str = ''
        if len(news) > 0:
            html_str += '<div class="news">%s 证监会新闻</div><br>\n' % day
            for i in news:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])
        if len(announcement) > 0:
            html_str += '<div class="news">%s 证监会新闻发布会</div><br>\n' % day
            for i in announcement:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])
        html_str += '\n'
        return html_str

    def have_news(self, day):
        news = self.all_data[day]['news']
        announcement = self.all_data[day]['announcement']
        if (len(news) > 0) | (len(announcement) > 0):
            return True
        else:
            return False


# FIXME buggy news gov
class NEWS_GOV:
    def __init__(self):
        self.today = get_today()
        self.s = requests.session()
        self.all_data = {}
        self.urls = dict(policy='http://www.gov.cn/zhengce/zuixin.htm',
                         bumen='http://www.gov.cn/zhengce/jiedu/bumen.htm',
                         zhuanjia='http://www.gov.cn/zhengce/jiedu/zhuanjia.htm',
                         meiti='http://www.gov.cn/zhengce/jiedu/meiti.htm')
        self.load()

    def _get_gov_policy_of_day(self, day, req_url):
        print("Fetching GOV Policy %s" % day)
        result = self.s.get(req_url, verify=False)
        b = result.content.decode('utf-8')
        soup = BeautifulSoup(b, 'lxml')
        c = soup.find('ul')
        d = c.findAll('li')
        parsed_list = []
        for item in d:
            link = item.find('a')['href']
            title = item.find('a').contents[0]
            date = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(item.find('span'))).group(1)
            if date == day:
                if req_url == self.urls['bumen']:
                    parsed_list.append({'link': 'http://www.gov.cn%s' % link, 'title': title, 'date': date})
                else:
                    parsed_list.append({'link': link, 'title': title, 'date': date})
        return parsed_list

    def fetch_all_of_day(self, day):
        try:
            len(self.all_data[day])
        except KeyError:
            policy = self._get_gov_policy_of_day(day, self.urls['policy'])
            bumen = self._get_gov_policy_of_day(day, self.urls['bumen'])
            zhuanjia = self._get_gov_policy_of_day(day, self.urls['zhuanjia'])
            meiti = self._get_gov_policy_of_day(day, self.urls['meiti'])

            self.all_data[day] = {'policy': policy,
                                  'bumen': bumen,
                                  'zhuanjia': zhuanjia,
                                  'meiti': meiti}

            with open('%s/news/gov/gov.pickle' % stock_data_root, 'wb') as f:
                pickle.dump(self.all_data, f, -1)

    def load(self):
        try:
            with open('%s/news/gov/gov.pickle' % stock_data_root, 'rb') as f:
                self.all_data = pickle.load(f)
        except FileNotFoundError:
            return {}
        except EOFError:
            return {}

    def generate_html_of_day(self, day):
        policy = self.all_data[day]['policy']
        bumen = self.all_data[day]['bumen']
        zhuanjia = self.all_data[day]['zhuanjia']
        meiti = self.all_data[day]['meiti']
        html_str = ''
        if len(policy) > 0:
            html_str += '<div class="news">%s 政府政策发布</div><br>\n' % day
            for i in policy:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])

        if len(bumen) > 0:
            html_str += '<div class="news">%s 部门解读</div><br>\n' % day
            for i in bumen:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])

        if len(zhuanjia) > 0:
            html_str += '<div class="news">%s 专家解读</div><br>\n' % day
            for i in zhuanjia:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])
        if len(meiti) > 0:
            html_str += '<div class="news">%s 媒体解读</div><br>\n' % day
            for i in meiti:
                html_str += '<a href="%s">%s</a><br>\n' % (i['link'], i['title'])
        html_str += '\n'
        return html_str

    def have_news(self, day):
        policy = self.all_data[day]['policy']
        bumen = self.all_data[day]['bumen']
        zhuanjia = self.all_data[day]['zhuanjia']
        meiti = self.all_data[day]['meiti']
        result = False

        if len(policy) > 0:
            result = True
        if len(bumen) > 0:
            result = True
        if len(zhuanjia) > 0:
            result = True
        if len(meiti) > 0:
            result = True
        return result


if __name__ == "__main__":
    src = NEWS_SRC()
    gov = NEWS_GOV()
    target_day = sys.argv[1]
    src.fetch_all_of_day(target_day)
    gov.fetch_all_of_day(target_day)
    result_html = generate_html(src.generate_html_of_day(target_day) + gov.generate_html_of_day(target_day))
    write_text_file('%s/news/%s.html' % (stock_data_root, target_day), result_html)
    if src.have_news(target_day) | gov.have_news(target_day):
        subprocess.call("./send_mail.py -n -s '610153443@qq.com' '今日要闻 %s' "
                       "'%s/news/%s.html'" % (stock_data_root, target_day, target_day), shell=True)
        subprocess.call("./send_mail.py -n -s 'zzy6548@126.com' '今日要闻 %s' "
                       "'%s/news/%s.html'" % (stock_data_root, target_day, target_day), shell=True)
        subprocess.call("./send_mail.py -n -s 'ustczyy@126.com' '今日要闻 %s' "
                       "'%s/news/%s.html'" % (stock_data_root, target_day, target_day), shell=True)
