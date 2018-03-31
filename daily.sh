#!/bin/bash
#python3 -m cmd_core.ctrl_script_hdl ctrls/everyday_update.ctrl
python3 -m cmd_core.ctrl_script_hdl ctrls/everyday_analysis.ctrl
python3 -m cmd_core.ctrl_script_hdl ctrls/everyday_analysis_v2.ctrl
python3 -m cmd_core.ctrl_script_hdl ctrls/anomaly.ctrl
#python3 -m cmd_core.ctrl_script_hdl ctrls/report.ctrl