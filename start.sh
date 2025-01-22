#!/bin/bash
# Install Chrome and ChromeDriver
apt-get update && apt-get install -y wget unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION.0/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/

# Make script executable and run it
python3 links.py
