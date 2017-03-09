import requests

req_url = 'http://flashhq.gtja.com'
get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
               'X-Requested-With':'ShockwaveFlash/24.0.0.221',
               'Cookie':'__v3_c_review_10890=0; __v3_c_last_10890=1487106962725; __v3_c_visitor=1487106909090118; Hm_lvt_1c5bee4075446b613f382dd399824571=1487106881,1488947837; Hm_lpvt_1c5bee4075446b613f382dd399824571=1488947837'}
get_params = {
    'type': 'GET_TICK_DETAILMAX',
    'exchange': 'sz', 'stockcode': '002263',
    'detailtype': 'max',
    'returnflag': 'max_first', 'from': 252, 'to': 0, 'radom': 0.29779909970238805

}
s = requests.session()
result = s.get(req_url, headers=get_headers, params=get_params, verify=False)
with open('/tmp/szse_company.xlsx', 'wb') as f:
    f.write(result.content)
