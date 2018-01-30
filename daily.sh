#!/bin/bash
python3 -m tools.ctrl_hdl ctrls/everyday_update.ctrl
python3 -m tools.ctrl_hdl ctrls/everyday_analysis.ctrl
python3 -m tools.ctrl_hdl ctrls/everyday_analysis_v2.ctrl
python3 -m tools.ctrl_hdl ctrls/anomaly.ctrl
cp ../stockdata/naive_score/*.csv ~/
cp ../stockdata/slice/*.csv ~/
eval `python3 -m -z misc.zip_report_send TODAY`
eval `python3 -m -s misc.zip_report_send TODAY`
rm ~/*.csv # todo: warning don't save any csv on ~/
