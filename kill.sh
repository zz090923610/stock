#!/bin/bash
sleep "$1"
kill `ps aux | grep sm.py | grep ./sm | grep -Po '\+\s[0-9]+\s' | tr -d ' +'`
