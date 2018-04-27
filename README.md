# stock
## Introduction:

stock sub-project is the major framework of the [anomaly](https://github.com/zz090923610/anomaly) project.

## Features:

## Why it's useful:

## Requirments:

## Getting started:


## Project structure:
```
stock
├── analysis
│   ├── models
│   ├── script_executor
│   │   ├── merge_data.py
│   │   ├── script_exec_hdl.py
│   │   ├── slice.py
│   │   └── TranslateHdl.py
│   └── tick
│       └── naive_summary.py
├── cmd_core
│   ├── cmd_parser.py
│   ├── ctrl_script_hdl.py
│   └── interactive_cmd_hdl.py
├── configs
│   └── conf.py
├── ctrls
│   └── your_own_workload.ctrl
├── misc
│   └── report_hdl.py
├── mkt_monitor
│   ├── alarm.py
│   ├── daemon.py
│   ├── monitorAPI.py
│   ├── rules.py
│   └── stock_feature.py
├── overview.py
├── scripts
│   └── your_own_preprocessing_script.txt
└── tools
    ├── communication
    │   └── mqtt.py
    ├── data
    │   ├── file_hdl.py
    │   ├── mkt_chn
    │   │   ├── fetch_day_level_quotes_china.py
    │   │   ├── fetch_symbol_list_china_a.py
    │   │   ├── fetch_tick_quotes_china.py
    │   │   └── symbol_list_china_hdl.py
    │   └── path_hdl.py
    ├── date_util
    │   └── market_calendar_cn.py
    └── io.py
```
## Extend system functionality by adding your own models:

## Setup automated workload:

## API Documents:
