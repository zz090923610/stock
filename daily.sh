#!/bin/bash

python3 -m tools.ctrl_executor.ctrl_script_hdl models/data_fetching/ctrls/everyday_update.ctrl

python3 -m tools.ctrl_executor.ctrl_script_hdl models/candle_stick_feature_extractor/ctrls/extract_candle_stick_features.ctrl

# python3 -m tools.ctrl_executor.ctrl_script_hdl models/candle_stock_analysis_legacy/ctrls/cond_freq_training.ctrl
python3 -m tools.ctrl_executor.ctrl_script_hdl models/candle_stock_analysis_legacy/ctrls/do_candle_stock_analysis.ctrl

# python3 -m tools.ctrl_executor.ctrl_script_hdl models/candle_stick_expected_total_return/ctrls/candlestick_total_ret_train.ctrl
python3 -m tools.ctrl_executor.ctrl_script_hdl models/candle_stick_expected_total_return/ctrls/candlestick_total_ret_eval.ctrl


python3 -m tools.ctrl_executor.ctrl_script_hdl models/money_tracing/ctrls/money_tracing.ctrl

python3 -m tools.ctrl_executor.ctrl_script_hdl models/tick_anomaly_filter/ctrls/anomaly.ctrl

python3 -m tools.ctrl_executor.ctrl_script_hdl models/report_sending/ctrls/report.ctrl
