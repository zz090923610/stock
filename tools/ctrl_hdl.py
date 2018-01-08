import os

import re

import sys

from tools.date_util.market_calendar_cn import MktCalendar

calendar = MktCalendar()


def load_script(script_path):
    if os.path.isfile(script_path):
        with open(script_path) as f:
            raw_script = f.readlines()
    else:
        raw_script = ''
    script = []
    for line in raw_script:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                script.append(split_line)
    for line in script:
        print(line)
    return script


def exec_ctrl_cmd(line):
    cmd = line
    if cmd[0] == "MERGE":
        import analysis.script_executor.merge_data as md
        md.script_exec(" ".join(cmd[1:]))
    elif cmd[0] == "SCRIPT":
        from analysis.script_executor.parser import engine
        engine(cmd[1])
    elif cmd[0] == "FETCH":
        if cmd[1] == "OHCL":
            from tools.fetch_day_level_quotes_china import DayLevelQuoteUpdaterTushare
            a = DayLevelQuoteUpdaterTushare()
            a.get_data_all_stock(start=calendar.validate_date(cmd[2]), end=calendar.validate_date(cmd[3]))
        elif cmd[1] == "TICK":
            from tools.fetch_tick_quotes_china import TickQuoteUpdaterTushare
            tick = TickQuoteUpdaterTushare()
            tick.get_tick_multiple(tick.symbol_list_hdl.symbol_list, [calendar.validate_date(cmd[2])])
        elif cmd[1] == "SYMBOL":
            from tools.internal_func_entry import update_symbol_list
            update_symbol_list()
    elif cmd[0] == "SLICE":
        from analysis.script_executor.slice import slice_all
        rename = True if cmd[4] == 'TRUE' else False
        slice_all(cmd[1], cmd[2], calendar.validate_date(cmd[3]), rename)
    elif cmd[0] == "NAIVESCORE":
        from analysis.script_executor.naive_score import calc_score_amount
        calc_score_amount("summary", calendar.validate_date(cmd[1]))
        from analysis.script_executor.naive_score import calc_score_turnover
        calc_score_turnover("summary", calendar.validate_date(cmd[1]))


if __name__ == '__main__':
    script = load_script(sys.argv[1])
    for l in script:
        exec_ctrl_cmd(l)