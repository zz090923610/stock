from tools.date_util.market_calendar_cn import MktCalendar

calendar = MktCalendar()


def exec_ctrl_cmd(line):
    cmd = line.split(" ")
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
            tick.get_tick_multiple(tick.symbol_list_hdl.symbol_list, calendar.validate_date(cmd[2]))
        elif cmd[1] == "SYMBOL":
            from tools.internal_func_entry import update_symbol_list
            update_symbol_list()
