#!/bin/bash
sudo apt-get install python3-dev python3-pip python3-tk

sudo pip3 install --upgrade pandas
sudo pip3 install --upgrade tushare
sudo pip3 install --upgrade bs4
sudo pip3 install --upgrade tzlocal
sudo pip3 install --upgrade matplotlib
sudo pip3 install --upgrade pillow
sudo pip3 install --upgrade bypy
sudo pip3 install --upgrade pylzma
sudo pip3 install --upgrade termcolor
sudo pip3 install --upgrade scipy
sudo pip3 install --upgrade xlrd
sudo pip3 install --upgrade scoop
sudo pip3 install --upgrade lxml requests
sudo ./install_font.sh

#chmod 700 ~/.ssh/authorized_keys
#sudo apt-get install samba smbclient cifs-utils
#mkdir -p /home/zhangzhao/data
#sudo mount -t cifs //192.168.0.105/data /home/zhangzhao/data -o user=zhangzhao -o pass=''

