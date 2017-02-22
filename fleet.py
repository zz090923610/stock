#!/usr/bin/python3
import json

import requests
from bs4 import BeautifulSoup

# window log 0
s = requests.session()
req_url = 'http://api.3kwan.cn'
# k: md5sum (from_id +'#' + ad_id + '#' + current_time_millis)
params = {'ac': 'window_log', 'sdk': 'a', 'k': 'a56b61752d142504d66fbc302077fd74', 'ct': 'log', 'version': '3.5'}

post_data = {"timestamp": "1487699872025", "screen": "900*1600", "phone_type": "GT-I9500",
             "from_id": "4601", "ad_id": "324", "sysversion": "4.4.2", "operators": "CM",
             "sdk": "a", "type": "1", "has_sd": "0", "net": "wifi", "version": "3.5",
             "mobile": "ef556d396579a23493228bb0e2a6af0d"}

headers = {'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)'}
result = s.post(req_url, data=json.dumps(post_data), params=params, headers=headers)
status_code = json.loads(result.text)['code']

# login

s = requests.session()
req_url = 'http://api.3kwan.cn'
params = {'ac': 'init_login', 'u': 'C3AB006D92BC61AAB1A870095E63C564A4540483A6086D7DAC1BC64F5506DF67', 'sdk': 'a',
          's': '47vdrqrq5c', 'k': '0028F38E2A87BDBDC9E510B51CF17943', 'ct': 'user', 'version': '3.5'}
headers = {'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)'}
result = s.post(req_url, params=params, headers=headers)
status_code = json.loads(result.text)['code']





req_url = 'http://bigship-3k-in.raygame1.com/tankheroclient/getconfig.php?'
get_params = dict(country='cn', plat='9001001', pkg=16, chid='0_4601')
result = s.post(req_url, data=post_data, params=params)
a = json.loads(result.text)
b = result.content.decode('utf-8')

soup = BeautifulSoup(b, 'lxml')

#       c = soup.find("div", {"id": "documentContainer"})
#       d = c.findAll('li')
#       parsed_list = []
#       for item in d:
#           ori_link = item.find('a')['href']
#           link = 'http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd' + \
#                  re.search(r"^.(/[a-zA-Z0-9/._]+)", ori_link).group(1)
#           title = item.find('a')['title']
#           date = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", str(item.find('span'))).group(1)
#           if date == day:
#               parsed_list.append({'link': link, 'title': title, 'date': date})
#       return parsed_list
