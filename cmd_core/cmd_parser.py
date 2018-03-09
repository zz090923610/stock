def exec_ctrl_cmd(line, calendar):
    cmd = line
    if cmd[0] == "MERGE":
        from analysis.script_executor.merge_data import cmd_merge
        cmd_merge(cmd[1], cmd[2], cmd[3])
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
            print(calendar.validate_date(cmd[2]))
            tick.get_tick_multiple(tick.symbol_list_hdl.symbol_list, [calendar.validate_date(cmd[2])])
        elif cmd[1] == "SYMBOL":
            from tools.fetch_symbol_list_china_a import update_symbol_list
            update_symbol_list()
    elif cmd[0] == "SLICECOMBINE":
        from analysis.script_executor.slice import slice_combine
        rename = True if cmd[4] == 'TRUE' else False
        slice_combine(cmd[1], cmd[2], calendar.validate_date(cmd[3]), rename)
    elif cmd[0] == "NAIVESCORE":
        if cmd[1] == "TURNOVER":
            from analysis.models.naive_score import naive_score_turnover
            naive_score_turnover(cmd[2], calendar.validate_date(cmd[3]))
        elif cmd[1] == "AMOUNT":
            from analysis.models.naive_score import naive_score_amount
            naive_score_amount(cmd[2], calendar.validate_date(cmd[3]))
    elif cmd[0] == "NAIVETICKSUMMARY":
        from analysis.tick.naive_summary import naive_summary_tick
        naive_summary_tick([calendar.validate_date(cmd[1])])
    elif cmd[0] == "CONDFREQ":
        if cmd[1] == "TRAIN":
            from analysis.models.conditional_frequency import cond_freq_train
            params = " ".join(cmd[4:])
            cond_freq_train(cmd[2], cmd[3], params)
