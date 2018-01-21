#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y unzip openjdk-8-jre-headless xvfb libxi6 libgconf-2-4

# Install ChromeDriver.
wget -N https://chromedriver.storage.googleapis.com/`curl -sS http://cdn.npm.taobao.org/dist/chromedriver/LATEST_RELEASE`/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip
sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver

