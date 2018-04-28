# stock
## Introduction:

stock sub-project is major part of [anomaly](https://github.com/zz090923610/anomaly) project.

## Features:
* Fetch day level / tick level trade history data of all symbols listed on SSE, SZSE.
* Do realtime market monitoring, alerting, automated trading based on customized rules.
* Make data preprocessing much easier by using scripts written in a customizable datasheet manuplate language.
* Embed your own models into this framework, by exporting it to control commands set.
* Automate all your workloads by writing control sequence script.

## Why do we need this:

Individual equity traders lack information and power to process information compared with institutional traders. Technical analysis is an easy but important way for them to follow the trend, probably created by those institutions. I saw lots of individual do this using Excel. It's okay if you only care about several stocks and apply same Excel operations on their data everyday, but what if you want to do some analysis for all those listed stocks? Can you filter out some of them given some kind of rules? Say if you have some interesting models, do you want your computer apply them for you everyday instead of do everything on your own? That's why Anomaly is created. This tool set try it best to not convey functions you can easily acquire from other shining softwares, but something to save you sometime.


## Requirments:

* Tested on Ubuntu 17.10 and python 3.6.2. All other apt, pip dependencies can be easily installed follow below instructions.
* More than 4GB free space should be enough if your models don't generate much data.

## Getting started:

* Download source code:
```shell
cd ~
git clone git@github.com:zz090923610/stock.git
cd stock
```
* Generate third-party dependency install commands:
```shell
python3 -m overview -d
```
something like below should be printed out:
```shell
sudo apt-get install -y mosquitto mosquitto-clients python3-pip cython3 zip
sudo -H pip3 install schedule pandas requests xlrd pytz paho-mqtt beautifulsoup4 lxml pillow
sudo -H pip3 install tushare
```
then install them manually.
* Configure data root.

Please edit second line of ./configs/conf.py, pass some valid FULL path of the directory you want to store all data generated by Anomaly.
```python
user_defined_data_root = "some/full/path/of/directory"
```
Or you can skip this step, then Anomayl will use default data root path, which is ~/data/stock_data for Linux and $user/Documents/stock_data for windows.

The final step is build command cache:
```shell
python3 -m overview -c
```
Something like this should be printed:
```shell
Updating command cache
# CMDEXPORT ( MERGE {path_from} {path_to} {index} ) cmd_merge
# CMDEXPORT ( SLICECOMBINE {input_path} {out_path} {date} {rename} ) slice_combine
# CMDEXPORT ( RENAMECOL {file_path} ) rename_column_title
# CMDEXPORT ( SCRIPT {script_path}) exec_script
# CMDEXPORT ( NAIVESCORE TURNOVER {data} {date}) naive_score_turnover
# CMDEXPORT ( NAIVESCORE AMOUNT {data} {date}) naive_score_amount
# CMDEXPORT ( CONDFREQ TRAIN {model_name} {use_dir} {params[4:]} ) cond_freq_train
# CMDEXPORT ( NAIVETICKSUMMARY {date} ) naive_summary_tick
# CMDEXPORT ( FETCH TICK {date_or_dates} ) update_tick_quotes
# CMDEXPORT ( FETCH OHCL {start_date} {end_date} ) update_day_level_quotes
# CMDEXPORT ( FETCH SYMBOL ) update_symbol_list
# CMDEXPORT ( ZIP {output_path} {input_path_list_str[2:]} ) zip_files
# CMDEXPORT ( SEND FILE WECHAT {path} {to} ) send_file_wechat
Found 13 commands
```
These are all available commands currently exported from all modules. We will see how to use them and how to customize them below. Just remember please build cache every time after you customize them.

Then you are ready to roll. Please refer to below writeups to start your workload quickly:
* [How to fetch raw OHCL/Tick data]()
* [How to do candle stick shape analysis]()
* [How to automate everything]()
* [Difference between control batch file and pre-proc script file]()
* [how to use your own models]()
## Project structure:
```
stock
├── analysis: all analysis related codes should go here.
│   ├── models
│   ├── script_executor
│   └── tick
├── cmd_core: codes for exec control batch file and control commands.
├── configs: settings go here.
├── ctrls: your own control batch files should be stored here.
├── misc: useful things which cannot find a better place to place.
├── mkt_monitor: codes about realtime market monitoring, rules, actions.
├── overview.py: the only python file doesn't depend on third-party codes even other codes within this project. Focusing 
|                on resolving third-party software dependency, finding TODOs, building command cache by tracing marked
|                comment marcos.
├── scripts: your_own_preprocessing_script.txt should goes here.
└── tools: important codes don't related to analysis and market monitoring.
    ├── communication
    ├── data: data related codes, data fetching, data IO, etc..
    │   └── mkt_chn: operations for different market should be store in separate folders.
    └── date_util: makret calendars for different markets should go here.
```

## API Documents:
