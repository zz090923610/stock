#!/usr/bin/python3
import pickle
import re
import subprocess
from datetime import datetime, timedelta
import sys
import time
import requests
from bs4 import BeautifulSoup

from common_func import get_today, get_time_of_a_day, generate_html


def write_text_file(file, content):
    with open(file, 'wb') as f:
        f.write(content.encode('utf8'))


def sleep_until(when):
    h, m, s = int(when.split(':')[0]), int(when.split(':')[1]), int(when.split(':')[2])
    date_today = get_today()
    next_wake_up_time = datetime(int(date_today.split('-')[0]), int(date_today.split('-')[1]),
                                 int(date_today.split('-')[2]), h,
                                 m, s) + timedelta(days=1)
    local_date = get_today()
    local_time = get_time_of_a_day()
    ln = datetime(int(local_date.split('-')[0]), int(local_date.split('-')[1]), int(local_date.split('-')[2]),
                  int(local_time.split(':')[0]), int(local_time.split(':')[1]), int(local_time.split(':')[2]))
    seconds = next_wake_up_time - ln
    print("now is " + get_time_of_a_day())
    print("sleeping %d" % seconds.seconds)
    time.sleep(seconds.seconds)


class NEWS_SRC:
    def __init__(self):
        self.today = get_today()
        self.s = requests.session()
        self.all_data = {}
        self.load()

    def _get_src_news_of_day(self, day):
        print("Fetching SRC news %s" % day)
        req_url = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd/index.html'
        result = self.s.get(req_url)
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
        result = self.s.get(req_url)
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
            with open('../stock_data/news/zjh/zjh.pickle', 'wb') as f:
                pickle.dump(self.all_data, f, -1)

    def load(self):
        try:
            with open('../stock_data/news/zjh/zjh.pickle', 'rb') as f:
                self.all_data = pickle.load(f)
        except FileNotFoundError:
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
        result = self.s.get(req_url)
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
                parsed_list.append({'link': link, 'title': title, 'date': date})
        return parsed_list

    def fetch_all_of_day(self, day):
        try:
            _ = self.all_data[day]
        except KeyError:
            policy = self._get_gov_policy_of_day(day, self.urls['policy'])
            bumen = self._get_gov_policy_of_day(day, self.urls['bumen'])
            zhuanjia = self._get_gov_policy_of_day(day, self.urls['zhuanjia'])
            meiti = self._get_gov_policy_of_day(day, self.urls['meiti'])

            self.all_data[day] = dict(policy=policy,
                                      bumen=bumen,
                                      zhuanjia=zhuanjia,
                                      meiti=meiti)
            with open('../stock_data/news/gov/gov.pickle', 'wb') as f:
                pickle.dump(self.all_data, f, -1)

    def load(self):
        try:
            with open('../stock_data/news/gov/gov.pickle', 'rb') as f:
                self.all_data = pickle.load(f)
        except FileNotFoundError:
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


if __name__ == "__main__":
    src = NEWS_SRC()
    gov = NEWS_GOV()
    target_day = sys.argv[1]
    src.fetch_all_of_day(target_day)
    gov.fetch_all_of_day(target_day)
    result_html = generate_html(src.generate_html_of_day(target_day) + gov.generate_html_of_day(target_day))
    write_text_file('../stock_data/news/%s.html' % target_day, result_html)
    subprocess.call("./send_mail.py -n -s '610153443@qq.com' '今日要闻 %s' "
                    "'../stock_data/news/%s.html'" % (target_day, target_day), shell=True)
    subprocess.call("./send_mail.py -n -s 'zzy6548@126.com' '今日要闻 %s' "
                    "'../stock_data/news/%s.html'" % (target_day, target_day), shell=True)
