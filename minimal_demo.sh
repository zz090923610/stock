#!/bin/bash
python3 -m cmd_core.ctrl_script_hdl ctrls/everyday_update.ctrl
python3 -m cmd_core.ctrl_script_hdl ctrls/cond_freq_training.ctrl
python3 -m cmd_core.ctrl_script_hdl ctrls/minimal_csa.ctrl