#!/bin/bash

cp ./msyh.ttf /tmp/msyh.ttf
rm -rf ~/.cache/matplotlib/*.cache
sudo cp /tmp/msyh.ttf /usr/local/lib/python3.5/dist-packages/matplotlib/mpl-data/fonts/ttf/
sudo cp ./matplotlibrc /usr/local/lib/python3.5/dist-packages/matplotlib/mpl-data/matplotlibrc