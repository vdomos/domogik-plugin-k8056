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

Coomand on,off relay of K8056 board With xPL Messages

	Technical Description of K8056 Board serial protocol

	Port RS232 is configure with this setting: 2400/8/n/1
	To control the k8056 card, the correct sequence needs to be send like this:
	Ascii code 13
	Card address (1..255)
	Instruction (see below), only supported now 'S'|'C'|'T' set/clear/toggle
	Relay #('1'..'9'), 9 for all relay. 
	Checkum, it is the 2-complement of the sum of the 4 previous bytes + 1. 
		In Python, checksum = ( 255 - (13 + int('1') + ord('S') + ord('1')) % 256 ) + 1

	Instructions:
	'E': Emergency stop all cards.
	'D': Display address of all cards in a binary fashion (LD1:MSB, LD8:LSB)
	'S': Set a relay, followed by relay # ('1'..'9' in ASCII), 9 for all relay.
	'C': Clear a relay, followed by relay # ('1'..'9' in ASCII), 9 for all relay.
	'T': Toggle a relay, followed by relay # ('1'..'8' in ASCII).
	'A': Change the current address of a card, followed by the address (1..255)
	'F': Force all cards address to 1 (default)
	'B': Send a byte, Allows to control the 8 relays in 1 byte (LD1:MSB, LD8:LSB) 


Implements
==========

@author: domos  (domos p vesta at gmail p com)
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import serial
import traceback
import time


class K8056Exception(Exception):
	"""
	K8056 exception
	"""

	def __init__(self, value):
		Exception.__init__(self)
		self.value = value

	def __str__(self):
		return repr(self.value)



class K8056:
	""" Open k8056 port
	"""

	def __init__(self, log):
		""" Create handler
		"""
		self._log = log


	def open(self, device):
		""" 
		Open k8056 device
		@param device : The full path of the device where serial is connected
		"""
		self._log.info("### Opening k8056 device : %s" % device)
		try:
			self._ser = serial.Serial(device, 2400,timeout=1)
			self._log.info("### k8056 port opened")
		except:
			error = "Error while opening k8056 device : %s : %s" % (device, str(traceback.format_exc()))
			raise K8056Exception(error)


	def write(self, address, relay, command):
		""" 
		Write command to K8056 board
		@param address : card address of K8056 board
		@param relay :   relay number of K8056 board
		@param command : relay command for K8056 board
		"""
		instructions = { '1': 'S', '0': 'C' }	  # Conversion 'command' xpl command to k8056 instructions.
	
		self._log.debug("### Write command '%s' to relay #%s on K8056 board #%d." % (command, relay, address) )

		checksum = ( 255 - (13 + address + ord(instructions[command]) + ord(relay)) % 256 ) + 1
		k8056_command = chr(13) + chr(address) + instructions[command] + relay + chr(checksum)
	
		self._log.debug("### Trame send to K8056 board: %s %s %s %s %s" % ( hex(13), hex(address), hex(ord(instructions[command])), hex(ord(relay)), hex(checksum)) )

		for k8056_trame_number in range(5):
			try:
				self._ser.write(k8056_command)				# Command be send 5x to be understand by K8056 Board (Velleman documentation)
			except:
				error = "Error while writing to k8056 device"
				raise K8056Exception(error)
	

	def close(self):
		""" close k8056 device
		"""
		self._log.info("### Close k8056 device")
		try:
			self._ser.close()
		except:
			error = "Error while closing k8056 device"
			raise K8056Exception(error)



