# -*- coding: utf-8 -*

#############################################################################
#	Copyright (C) 2018  Luciano del Valle	@lucdelcan 						#
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

import shodan
import sys, json
from logging import getLogger, ERROR
from pymongo import MongoClient
from bson import json_util
from datetime import datetime
from time import strftime
import time


# You should insert your shodan api key here
SHODAN_API_KEY = ""

api = shodan.Shodan(SHODAN_API_KEY)


client= MongoClient()
db= client.Octopus


class colors:
	HEADER = '\033[93m'
	FAIL = '\033[91m'
	SUCCES = '\033[92m'
	REGULAR = '\033[0m'

def buscar(cadena):
	try:
		resultado=api.search(str(cadena))
		return resultado
	except Exception as e:
		print "Error during the search: %s" %e
		resultado=[]
		return resultado

def insert_mongodb(py_dic):
	if py_dic != "nothing to add":
		try:
			date_Insert = time.strftime("%H:%M:%S - %d/%m/%Y %Z")
			py_dic['date_Insert'] = date_Insert


			host_db = db.hosts.find_one({'host':py_dic['host']})
			if host_db is None:
				db.hosts.insert({'host':py_dic['host'],'date_Insert':py_dic['date_Insert'],'credentials':py_dic['credentials'],
				'location':py_dic['location'], 'status':py_dic['status'],'open_ports':py_dic['open_ports'], "info":py_dic['info']})
			else:
				db.hosts.update({'host':py_dic['host']},{'$set':{'date_Insert':py_dic['date_Insert'], 'location':py_dic['location'],'status':py_dic['status'],
				'open_ports':py_dic['open_ports']}},True)

			print colors.SUCCES + "[INFO] DATA INSERTED IN DB" + colors.REGULAR
		except Exception, e:
			print e
			print colors.FAIL + "[WARNING] ERROR INSERTING IN MONGODB" + colors.REGULAR
	else:
		print colors.HEADER + "[INFO] NO DATA TO INSERT" + colors.REGULAR


def insert_mongo(py_dic):
	if py_dic != "nothing to add":
		try:
			date_Insert = time.strftime("%H:%M:%S - %d/%m/%Y %Z")
			py_dic['date_Insert'] = date_Insert
			json_object = json.dumps(py_dic)
			cursor = db.hosts.insert(json_util.loads(json_object))
			print colors.SUCCES + "[INFO] DATA INSERTED IN DB" + colors.REGULAR
		except Exception, e:
			print e
			print colors.FAIL + "[WARNING] ERROR INSERTING IN MONGODB" + colors.REGULAR
	else:
		print colors.HEADER + "[INFO] NO DATA TO INSERT" + colors.REGULAR



def def_service(port):
	if port == 80:
		service = 'http'
	elif port == 20:
		service = 'ftp-data'
	elif port == 21:
		service = 'ftp'
	elif port == 22:
		service = 'ssh'

	return service


def iotscan(resul):
	res = buscar(resul)
	dichost = {"ip":"", "date_Insert":"", "credentials":{}, "location": {},"status":"" ,"open_ports":{}, "info":{}}
	dic = {"ip":"","hostname":"", "status":"", "date_Insert":"","open_ports":{}, "credentials":{}}
	dic_port= {}
	all_ips = []
	all_dics = []
	all_dics_host =[]
	alldics = {}
	dic_credentials = {"ssh_user":"blocked", "ssh_pass":"blocked", "ftp_user":"blocked", "ftp_pass":"blocked","telnet_user":"blocked","telnet_pass":"blocked"}
	info = {"python":"True", "os":""}

	if len(res) !=0:
		print 'Cantidad de resultados encontrados: %s'% res['total']
		for i in res['matches']:
			print 'IP: %s' %i.get('ip_str')
			print 'Puerto: %s' %i.get('port')
			print 'O.S: %s' %i.get('os','Unknown')
			print 'Hostnames: %s' %i.get('hostnames')
			print 'City: %s' %i.get('city', 'Unkonwn')
			print 'Latitude: %s' %i.get('latitude', 'Unknown')
			print 'Longitude: %s' %i.get('Longitude', 'Unknown')
			print 'Last update: %s' %i.get('updated')
			print i['data']
			print ''
			dic_info = {'python':"True", 'os':i.get('os')}
			dic = {'ip': i.get('ip_str'),'hostname': i.get('hostname'), 'status': "up", 'open_ports':i.get('port'), 'credentials':dic_credentials}
			dichost = {'host': i.get('ip_str'),'credentials':dic_credentials, 'location': i.get('city'), 'status': "up", 'open_ports':i.get('port'),'info':dic_info }

			insert_mongodb(dichost)
			all_dics.append(dichost)

	return all_dics
