#!/usr/bin/env python
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

from werkzeug.security import generate_password_hash
from pymongo import MongoClient
client = MongoClient()
db = client.Octopus

username = raw_input("usuario: ")
passw = raw_input("contraseña: ")


user={"_id":username, "password":generate_password_hash(passw, method='pbkdf2:sha256'),"status":1}
db.users.insert(user)
