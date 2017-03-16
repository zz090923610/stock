#!/bin/bash
sudo sh ./requirements_apt.txt
sudo pip3 install -r ./requirements.txt
sudo ./stock/common/install_font.sh
python3 ./init_path.py


#chmod 700 ~/.ssh/authorized_keys
#sudo apt-get install samba smbclient cifs-utils
#mkdir -p /home/zhangzhao/data
#sudo mount -t cifs //192.168.0.105/data /home/zhangzhao/data -o user=zhangzhao -o pass=''

