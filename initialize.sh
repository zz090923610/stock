#!/bin/bash
sudo sh ./requirements_apt.txt
sudo pip3 install --upgrade pip
sudo pip3 install pandas
sudo pip3 install Cython==0.23
sudo pip3 install -r ./requirements.txt
sudo pip3 install tushare
sudo apt-get -y install python-kivy-examples
cd ./stock/common
sudo ./stock/common/install_font.sh
cd ../..
su zhangzhao -c "python3 ./init_path.py"
sudo echo "sslocal -s '115.28.142.56' -p '8388' -b '127.0.0.1' -l '1080' -k 'zz90q9d3' -m 'aes-256-cfb' &" >> /etc/rc.local

#chmod 700 ~/.ssh/authorized_keys
#sudo apt-get install samba smbclient cifs-utils
#mkdir -p /home/zhangzhao/data
#sudo mount -t cifs //192.168.0.105/data /home/zhangzhao/data -o user=zhangzhao -o pass=''

