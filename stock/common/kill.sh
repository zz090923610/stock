#!/bin/bash
sleep "$1"
kill `ps aux | grep ffplay | grep "loop" | grep -Po '\+\s[0-9]+\s' | tr -d ' +'`
