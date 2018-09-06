#! /usr/bin/python
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

import sys, GeoIP, nmap
from logging import getLogger, ERROR
getLogger("scapy.runtime").setLevel(ERROR)
from scapy.all import *
from subnetting import ip2network_address
from pymongo import MongoClient
from datetime import datetime
from time import strftime

gi = GeoIP.open("GeoLiteCity.dat", GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)

client = MongoClient()
db = client.Octopus

class colors:
	HEADER = '\033[93m'
	FAIL = '\033[91m'
	SUCCES = '\033[92m'
	REGULAR = '\033[0m'


def subnetting(ip, cidr):
	ip_range = ip2network_address(ip, cidr)
	number_ip = 2 ** (32 - int(cidr)) - 2
	box_ip = []

	if number_ip <= 256:  # ../24 or more
		red = ip_range[2].split('.')[0] + '.' + ip_range[2].split('.')[1] + '.' + ip_range[2].split('.')[2] + '.'
		start_ip = ip_range[3]
		end_ip = ip_range[4]
		start = int(ip_range[3].split('.')[3])
		end = int(ip_range[4].split('.')[3])
		for i in range(start, end + 2):
			box_ip.append(red + str(i))

	elif 256 < number_ip <= 65536:  # ../16 or more
		red = ip_range[2].split('.')[0] + '.' + ip_range[2].split('.')[1] + '.'
		oc4 = int(ip_range[3].split('.')[3])
		oc3 = int(ip_range[3].split('.')[2])
		for i in range(0, number_ip):
			box_ip.append(red + str(oc3) + '.' + str(oc4))
			if oc4 == 255:
				oc4 = -1
				oc3 += 1
			oc4 += 1
	elif 65536 < number_ip <= 16777216:  # ../8 or more
		red = ip_range[2].split('.')[0] + '.'
		oc2 = int(ip_range[2].split('.')[1])
		oc3 = int(ip_range[3].split('.')[2])
		oc4 = int(ip_range[3].split('.')[3])
		for i in range(0, number_ip):
			box_ip.append(red + str(oc2) + '.' + str(oc3) + '.' + str(oc4))
			if oc3 == 255:
				if oc4 == 255:
					oc2 += 1
			if oc4 == 255:
				oc4 = -1
				if oc3 < 255:
					oc3 += 1
				else:
					oc3 = 0
			oc4 += 1

		else:
			print colors.FAIL + '[WARNING] THE MAXIMU CIDR BLOCK ALLOWED IS /8' + colors.REGULAR

	return box_ip


def range_ip(h):
	h = h.split('-')
	net = h[0].split('.')
	last = int(h[1])
	first = int(net[3])
	net = net[0] + '.' + net[1] + '.' + net[2] + '.'
	all_hosts = []

	for i in range(first, last + 1):
		all_hosts.append(net + str(i))

	return all_hosts


def checkhost(ip):
	conf.verb = 0
	try:
		ping = sr1(IP(dst=ip) / ICMP(), timeout=2)
		if ping is None:
			return False
		else:
			return True
	except Exception:
		return False

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


def os_fingerprint(host):
	try:
		nm = nmap.PortScanner()
		res = nm.scan(hosts=host, arguments='-n -O -T4 -p 22, 80')
		os = res['scan'][host]['osmatch'][0]['osclass'][0]['osfamily']
		return os
	except Exception, error:
		print error
		print colors.FAIL + "[WARNING] CANNOT DETERMINATE OS" + colors.REGULAR

def insert_mongodb(py_dic):
	if py_dic != "nothing to add":
		try:
			date_Insert = time.strftime("%H:%M:%S - %d/%m/%Y %Z")
			py_dic['date_Insert'] = date_Insert
			info = {"python":"False", "os":py_dic["os"]}

			host_db = db.hosts.find_one({'host':py_dic['host']})
			if host_db is None:
				db.hosts.insert({'host':py_dic['host'],'date_Insert':py_dic['date_Insert'],'credentials':py_dic['credentials'],
				'location':py_dic['location'], 'status':py_dic['status'],'open_ports':py_dic['open_ports'], "info":info})
			else:
				db.hosts.update({'host':py_dic['host']},{'$set':{'date_Insert':py_dic['date_Insert'], 'location':py_dic['location'],'status':py_dic['status'],
				'open_ports':py_dic['open_ports']}},True)

			print colors.SUCCES + "[INFO] DATA INSERTED IN DB" + colors.REGULAR
		except Exception, e:
			print e
			print colors.FAIL + "[WARNING] ERROR INSERTING IN MONGODB" + colors.REGULAR
	else:
		print colors.HEADER + "[INFO] NO DATA FOUND TO INSERT" + colors.REGULAR


def netscan(listahost):
	try:
		dic = {"host":"", "status":"", "date_Insert":"", "open_ports":{}, "credentials":{}}
		dic_ports = {}
		dic_credentials = {"ssh_user":"none", "ssh_pass":"none", "ftp_user":"none", "ftp_pass":"none"}

		all_hosts = []
		all_dics = []
		ports = [80, 20, 21, 22]

		if listahost.find('/') != -1:
			all_hosts += subnetting(listahost.split('/')[0], listahost.split('/')[1])
		elif listahost.find('-') != -1:
			all_hosts += range_ip(listahost)
		elif listahost.find(',') != -1:
			all_hosts += listahost.split(',')
		else:
			all_hosts.append(listahost)

		start_clock = datetime.now()
		SYNACK = 0x12
		#2RSTACK = 0x14
		srcport = RandShort()
		conf.verb = 0
		for h in all_hosts:
			if checkhost(h):
				dic = {'host': h, 'status': "up"}
				location = gi.record_by_name(h)
				dic['location'] = location
				dic['os'] = os_fingerprint(h)
				print colors.HEADER + "Scanning " + h + " at: " + strftime("%H:%M:%S") + colors.REGULAR
				for p in ports:
					# ------------- ACK SCAN -------------
					SYNACKpkt = sr1(IP(dst=h) / TCP(sport=srcport, dport=p, flags="S"), timeout=4)
					if SYNACKpkt is not None:
						pktflags = SYNACKpkt.getlayer(TCP).flags
						if pktflags == SYNACK:
							service = def_service(p)
							dic_ports[str(p)]=service
							print colors.SUCCES + "Port " + str(p) + ": Open" + colors.REGULAR
						RSTpkt = IP(dst=h) / TCP(sport=srcport, dport=p, flags="R")
						send(RSTpkt)
					# ---------------------------

				if dic_ports!={}:
					dic['open_ports'] = dic_ports
					dic['credentials'] = dic_credentials
					insert_mongodb(dic)
					all_dics.append(dic)
			else:
				print colors.FAIL + "Host " + h + " is down" + colors.REGULAR
		stop_clock = datetime.now()
		total_time = stop_clock - start_clock
		print colors.HEADER + "Scanning finished" + colors.REGULAR
		print colors.HEADER + "Total time: " + str(total_time) + colors.REGULAR
		return all_dics, total_time

	except Exception, error:
		print colors.FAIL + "An error was detected \n" + colors.REGULAR
		print error

	except KeyboardInterrupt:
		print colors.HEADER + "User requested shutdown... \n" + colors.REGULAR
		print colors.HEADER + "Exiting..." + colors.REGULAR
		sys.exit(1)
