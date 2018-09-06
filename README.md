<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1iOfCsb3mNlTd5sX-wnaWycOe6OKKrjxg"/>
</p>

#
This project is a ssh botnet, writen in python 2.7, that include a web panel that offers a few functionalities like network scan, brute force and ddos attacks, send files, execute of python scripts, etc. This code is for learning/researching purpose and I am not responsible for the illegal use of this software.

## Get started
In the first place you must to have installed <a href="https://www.python.org/download/releases/2.7/">Python 2.7</a>, <a href="https://pypi.org/project/pip/">pip</a> and <a href="https://www.mongodb.com/">MongoDB</a> >= 2.6.10 in your system.

### Installation
You must run the following commands in your bash terminal:
```bash
sudo apt install libgeoip
```
And inside Octopus folder:
```bash
sudo pip install -r requirements.txt
```
After that you have to run register user script, in order to register a new user to access to web panel:
```bash
python registry_user.py
```

### Usage
You must run the following command to run the application, Octopus have to run with sudo in order to use scapy:
```bash
sudo python octopus.py
```

## Modules
This is going to be a brief explanation of each modules of Octopus botnet. The results will be show in the console, in the web panel and will be stored in the database too.
### Net scanner
You can put in here an ip address, a range of ips or a CIDR block (max. length /8).
###  IOT scanner
This is an implementation of the Shodan API. If you want to use this module you should put your Shodan API key inside modules/iotscanner.py.
### SSH/FTP Brute
This module will launch a brute force attack over ssh or ftp protocol. You can put an IP address as target or launch attack over all the hosts that have open port 22 in your database.
### Upload files to C&C
Here you can upload files or scripts to the server, in order to send it later to the bots.
### Scripts Load
You can select one file that will be send to the target. You can choose run the file if is it a python script.
### Bot Panel
Here will be list all the bots that you have registed in your database. In this botnet a host will we called bot when you have registed his ssh credentials in the database. You can select one or more bots and launch load file and run script functionality, ddos attack or cryptominer.
### Botnet Map
This module will be show your bots in the world map.
### Results
Here will be show to results of the differents modules.

## Contributing
Anyone that want to improve this project will be welcome :) .
## Contact
- Twitter: <a href="https://twitter.com/JaviMrSec">@JaviMrSec</a>
