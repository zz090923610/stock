#!/bin/bash

[ "$1" = '-s' ] && killall ffplay 2>&1 >/dev/null  || {

	nohup ffplay -nodisp -loop 0 /usr/share/sounds/ubuntu/stereo/bell.ogg 2>&1 >>/dev/null &
}
