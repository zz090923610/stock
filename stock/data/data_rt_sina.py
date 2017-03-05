#!/usr/bin/python3
from pandas import DataFrame

from stock.common.common_func import *

TODAY = get_today()


def get_rt_data(once=500):
    s = requests.session()
    stock_list = []
    tmp_str = ''
    cnt = 0
    total_cnt = 0
    for stock in BASIC_INFO.symbol_list:
        tmp_str += '%s%s,' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
        cnt += 1
        if (cnt >= once) or (total_cnt == len(BASIC_INFO.symbol_list)):
            stock_list.append(tmp_str)
            tmp_str = ''
            cnt = 0
    tmp_result = ''
    for line in stock_list:
        req_url = 'http://hq.sinajs.cn/list=' + line
        get_headers = {'User-Agent': AGENT['User-Agent']}
        result = s.get(req_url, headers=get_headers, verify=False)
        if result.status_code != 200:
            print('Exception %d' % result.status_code)
        tmp_result += result.text
    result = re.sub(r'[\n\"]', '', tmp_result)
    result_list = result.split(";")
    final_list = []
    for line in result_list:
        parsed_line = parse_one_line(line)
        if parsed_line is not None:
            final_list.append(parsed_line)
    return final_list


def get_rt_data_dict():
    rt_list = get_rt_data()
    rt_dict = {}
    for line in rt_list:
        rt_dict.update({line['code']: line})
    return rt_dict


def get_rt_data_for_stock(s, stock):
    print('Getting real time %s' % stock)
    tmp_str = '%s%s' % ('sh' if BASIC_INFO.market_dict[stock] == 'sse' else 'sz', stock)
    req_url = 'http://hq.sinajs.cn/list=' + tmp_str
    get_headers = {'User-Agent': AGENT['User-Agent']}
    result = s.get(req_url, headers=get_headers, verify=False)
    if result.status_code != 200:
        print('Exception %d' % result.status_code)
    tmp_result = result.text
    result = re.sub(r'[\n\"]', '', tmp_result)
    result_line = result.split(";")[0]
    parsed_line = parse_one_line(result_line)
    if parsed_line is not None:
        if parsed_line['open'] == 0:
            return None
        b = DataFrame(parsed_line, index=[-1])
        return b[['date', 'open', 'high', 'close', 'low', 'volume']]
    else:
        return None


def get_pd_from_rt_data_dict_of_stock(rt_data_dict, stock):
    try:
        return DataFrame(rt_data_dict[stock], index=[-0])
    except KeyError:
        return None


def parse_one_line(line):
    try:
        reg_str = r'(var hq_str_[a-z]{2}([0-9]{6})=)'
        m = re.search(reg_str, line)
        to_replace = m.group(0)
        code = m.group(2)
        line = line.replace(to_replace, '%s,' % code)
        slitted_list = line.split(',')
        final_dict = dict(code=slitted_list[0],
                          open=float(slitted_list[2]),
                          close=float(slitted_list[4]),
                          high=float(slitted_list[5]),
                          low=float(slitted_list[6]),
                          volume=int(slitted_list[9]) / 100,
                          money_volume=float(slitted_list[10]) // 10000,
                          bid_1_size=int(slitted_list[11]) / 100,
                          bid_2_size=int(slitted_list[13]) / 100,
                          bid_3_size=int(slitted_list[15]) / 100,
                          bid_4_size=int(slitted_list[17]) / 100,
                          bid_5_size=int(slitted_list[19]) / 100,
                          bid_1_price=float(slitted_list[12]),
                          bid_2_price=float(slitted_list[14]),
                          bid_3_price=float(slitted_list[16]),
                          bid_4_price=float(slitted_list[18]),
                          bid_5_price=float(slitted_list[20]),
                          ask_1_size=int(slitted_list[21]) / 100,
                          ask_2_size=int(slitted_list[23]) / 100,
                          ask_3_size=int(slitted_list[25]) / 100,
                          ask_4_size=int(slitted_list[27]) / 100,
                          ask_5_size=int(slitted_list[29]) / 100,
                          ask_1_price=float(slitted_list[22]),
                          ask_2_price=float(slitted_list[24]),
                          ask_3_price=float(slitted_list[26]),
                          ask_4_price=float(slitted_list[28]),
                          ask_5_price=float(slitted_list[30]),
                          date=slitted_list[31],
                          time=slitted_list[32])
        final_dict['total_ask_size'] = sum([final_dict['ask_%d_size' % d] for d in range(1, 6)])
        final_dict['total_bid_size'] = sum([final_dict['bid_%d_size' % d] for d in range(1, 6)])
        return final_dict
    except IndexError:
        print(line)
        return None
    except AttributeError:
        print(line)
        return None


def print_a_dict(a_dict):
    rows, columns = [int(x) for x in os.popen('stty size', 'r').read().split()]
    print('=' * columns)
    print('%s %s [%s]' % (a_dict['date'], a_dict['time'], a_dict['code']))
    print('Open %.2f high %.2f low %.2f close/now %.2f' % (
        a_dict['open'], a_dict['high'], a_dict['low'], a_dict['close']))
    print('Total bid %d, Total ask %d' % (a_dict['total_bid_size'], a_dict['total_ask_size']))
    print('-' * columns)
    print('%.2f\t%d' % (a_dict['ask_5_price'], a_dict['ask_5_size']))
    print('%.2f\t%d' % (a_dict['ask_4_price'], a_dict['ask_4_size']))
    print('%.2f\t%d' % (a_dict['ask_3_price'], a_dict['ask_3_size']))
    print('%.2f\t%d' % (a_dict['ask_2_price'], a_dict['ask_2_size']))
    print('%.2f\t%d' % (a_dict['ask_1_price'], a_dict['ask_1_size']))
    print('-' * columns)
    print('%.2f\t%d' % (a_dict['biAttributeErrord_1_price'], a_dict['bid_1_size']))
    print('%.2f\t%d' % (a_dict['bid_2_price'], a_dict['bid_2_size']))
    print('%.2f\t%d' % (a_dict['bid_3_price'], a_dict['bid_3_size']))
    print('%.2f\t%d' % (a_dict['bid_4_price'], a_dict['bid_4_size']))
    print('%.2f\t%d' % (a_dict['bid_5_price'], a_dict['bid_5_size']))
    print('=' * columns)


def update_daily_list_today():
    tm = get_time_of_a_day()
    if tm >= '13:01:00':
        a = get_rt_data()
        for record in a:
            if record['code'] == '000001':
                print(record)
            update_daily_list_record(record['code'], record)


def update_daily_list_record(stock, record):
    final_record = dict(date=record['date'], open=record['open'], high=record['high'], close=record['close'],
                        low=record['low'],
                        volume=record['volume'])
    data_already_have = load_csv('%s/data/%s.csv' % (stock_data_root, stock))
    if final_record['date'] not in [i['date'] for i in data_already_have]:
        data_already_have.append(final_record)
    else:
        print(23333)
    b = pd.DataFrame(data_already_have)
    b = b.sort_values(by='date', ascending=True)
    column_order = ['date', 'open', 'high', 'close', 'low', 'volume']
    b[column_order].to_csv('%s/data/%s.csv' % (stock_data_root, stock), index=False)
