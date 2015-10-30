#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

K8056 relay board management 
K8056 is a 8-CHANNEL RELAY CARD Velleman kit 
See k8056 manual on Velleman web site for details: http://www.velleman.be/fr/en/product/view/?id=351282

Implements
==========

XplK8056Manager


@author: domos  (domos p vesta at gmail p com)
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.xplconnector import Listener
from domogik.xpl.common.plugin import XplPlugin

from domogik_packages.plugin_k8056.lib.k8056 import K8056
from domogik_packages.plugin_k8056.lib.k8056 import K8056Exception


class XplK8056Manager(XplPlugin):
	""" Send command to K8056 relay board from xpl message received
	"""

	def __init__(self):
		""" Init plugin
		"""
		XplPlugin.__init__(self, name='k8056')

		# check if the plugin is configured. If not, this will stop the plugin and log an error
		if not self.check_configured():
			return
			
		# Configuration
		device = self.get_config("k8056_device")				         # Serial port
		if device == None:
			self.log.error('### Device is not configured, exitting') 
			self.force_leave()
			return

		# Init relayboard
		self.k8056_board  = K8056(self.log)
		
		# Open serial port
		try:
			self.k8056_board.open(device)
		except K8056Exception as e:
			self.log.error(e.value)
			print(e.value)
			self.force_leave()
			return
			

		# Create listeners
		self.log.info("### Creating listener for K8056")    
		Listener(self.k8056_cmnd_cb, self.myxpl, {'xpltype': 'xpl-cmnd', 'schema': 'ac.basic'})	# ac.basic { address=0 unit=1 command=off }

		self.ready()



	def k8056_cmnd_cb(self, message):
		""" Call k8056 lib for sending command to board
			@param message : xpl message
			
			address (805600001..805600255) = address of k8056 board (1..255)
			unit = relay number of k8056 board (1..9), 9 is for all relay
			command = on, off
			
			See lib/k8056.py for technical description of K8056 Board serial protocol
		"""
		self.log.debug("### Call k8056_cmnd_cb")
		self.log.debug("### Command '%s' on relais #%s of board #%s" % (message.data['command'], message.data["unit"], message.data["address"]))

	
		board_address = int(message.data['address']) - 805600000
		if board_address not in range(1, 256):             			# Address of the card (1..255)
			self.log.warning("### Address not for k8056 board : %d" % board_address)
			return
		
		relay_number = message.data['unit']
		if int(relay_number) not in range(1,10):                	# Relay number ('1'..'9'), 9=all
			self.log.warning("### Bad relay number for k8056 board : %s" % relay_number)
			return
				
		command_relay = message.data['command']
		if command_relay not in ['on', 'off']:
			self.log.warning("### Bad command for k8056 board : %s" % command_relay)
			return

		# Write command to K8056 board
		self.k8056_board.write(board_address, relay_number, command_relay)
		
		# Send ACK xpl-trig message to xpl-cmnd command.
		self.log.debug("### Send xpl-trig msg to k8056 command")      # xpl-trig ac.basic { address=0 unit=1 command=off }
		mess = XplMessage()
		mess.set_type('xpl-trig')
		mess.set_schema('ac.basic')
		mess.add_data({'address'  :  message.data["address"]})
		mess.add_data({'unit'   :  message.data["unit"]})
		mess.add_data({'command'     : message.data['command']})
		self.myxpl.send(mess)


if __name__ == "__main__":
	XplK8056Manager()

