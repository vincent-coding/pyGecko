import socket, struct, re

def onlyCharactersIpAdd(ip):
	check = re.compile(r'[^0-9.]').search
	return not bool(check(ip))

def checkip(ip):
	pieces = ip.split('.')
	if len(pieces) != 4: return False
	try: return all(0<=int(p)<256 for p in pieces)
	except ValueError: return False

class uGecko:
	def __init__(self, ip):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		if not onlyCharactersIpAdd(ip): raise BaseException("The entered IP address is not only composed of numbers and dots.") 
		if not checkip(ip): raise BaseException("The entered IP address does not have a valid structure!")
		self.ip = ip
		self.connected = False

	def connect(self, timeout = 5):
		if self.ip == None or self.ip == "": raise BaseException("No ip address has been entered!")
		else:
			if not self.connected:
				try:
					self.socket.settimeout(timeout)
					self.socket.connect((str(self.ip), 7331))
					self.socket.settimeout(None)
					self.connected = True
				except: raise BaseException(f"Unable to connect to {self.ip}!")
			else: raise BaseException("A connection is already in progress!")

	def disconnect(self):
		if self.connected:
			self.socket.close() # TODO: Make checks
			self.connected = False
		else: raise BaseException("No connection is in progress!")

	def isConnected(self):
		return self.connected

	def validRange(self, address, length):
		if   0x01000000 <= address and address + length <= 0x01800000: return True
		elif 0x0E000000 <= address and address + length <= 0x10000000: return True #Depends on game
		elif 0x10000000 <= address and address + length <= 0x50000000: return True #Doesn't quite go to 5
		elif 0xE0000000 <= address and address + length <= 0xE4000000: return True
		elif 0xE8000000 <= address and address + length <= 0xEA000000: return True
		elif 0xF4000000 <= address and address + length <= 0xF6000000: return True
		elif 0xF6000000 <= address and address + length <= 0xF6800000: return True
		elif 0xF8000000 <= address and address + length <= 0xFB000000: return True
		elif 0xFB000000 <= address and address + length <= 0xFB800000: return True
		elif 0xFFFE0000 <= address and address + length <= 0xFFFFFFFF: return True
		else: return False

	def validAccess(self, address, length, access):
		if   0x01000000 <= address and address + length <= 0x01800000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0x0E000000 <= address and address + length <= 0x10000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0x10000000 <= address and address + length <= 0x50000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return True
		elif 0xE0000000 <= address and address + length <= 0xE4000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xE8000000 <= address and address + length <= 0xEA000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xF4000000 <= address and address + length <= 0xF6000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xF6000000 <= address and address + length <= 0xF6800000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xF8000000 <= address and address + length <= 0xFB000000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xFB000000 <= address and address + length <= 0xFB800000:
			if access.lower() == "read" : return True
			if access.lower() == "write": return False
		elif 0xFFFE0000 <= address and address + length <= 0xFFFFFFFF:
			if access.lower() == "read" : return True
			if access.lower() == "write": return True
		else: return False

	def poke8(self, address, value, skip = False):
		if self.connected:
			if not skip:
				if not self.validRange(address, 1): raise BaseException("Address range not valid")
				if not self.validAccess(address, 1, "write"): raise BaseException("Cannot write to address")
			self.socket.send(b'\x01')
			req = struct.pack(">II", int(address), int(value))
			self.socket.send(req)
			return
		else: raise BaseException("No connection is in progress!")

	def poke16(self, address, value, skip = False):
		if self.connected:
			if not skip:
				if not self.validRange(address, 2): raise BaseException("Address range not valid")
				if not self.validAccess(address, 2, "write"): raise BaseException("Cannot write to address")
			self.socket.send(b'\x02')
			req = struct.pack(">II", int(address), int(value))
			self.socket.send(req)
			return
		else: raise BaseException("No connection is in progress!")

	def poke32(self, address, value, skip = False):
		if self.connected:
			if not skip:
				if not self.validRange(address, 4): raise BaseException("Address range not valid")
				if not self.validAccess(address, 4, "write"): raise BaseException("Cannot write to address")
			self.socket.send(b'\x03')
			req = struct.pack(">II", int(address), int(value))
			self.socket.send(req)
			return
		else: raise BaseException("No connection is in progress!")

	def serialPoke(self, addressTable, value, skip = False):
		if self.connected:
			if isinstance(addressTable, list):
				for address in addressTable:
					if not skip:
						if not self.validRange(address, 4): raise BaseException("Address range not valid")
						if not self.validAccess(address, 4, "write"): raise BaseException("Cannot write to address")
					self.socket.send(b"\x03")
					req = struct.pack(">II", address, value)
					self.socket.send(req)
				return
			else: raise BaseException("Address is not a list!")
		else: raise BaseException("No connection is in progress!")

	def writeString(self, address, string, skip = False):
		if self.connected:
			if type(string) != bytes: string = bytes(string, "UTF-8") #Sanitize
			if len(string) % 4: string += bytes((4 - (len(string) % 4)) * b"\x00")
			pos = 0
			for x in range(int(len(string) / 4)):
				self.poke32(address, struct.unpack(">I", string[pos:pos + 4])[0], skip)
				address += 4;pos += 4
			return
		else: raise BaseException("No connection is in progress!")

	def clearString(self, startAddress, endAddress, skip = False):
		if self.connected:
			length = endAddress - startAddress
			i = 0
			while i <= length:
				self.poke32(startAddress + i, 0x00000000, skip)
				i += 4
			return
		else: raise BaseException("No connection is in progress!")

	def readString(self, address, length, skip = False):
		if self.connected:
			string = self.read(address, length, skip)
			return string.decode('UTF-8')
		else: raise BaseException("No connection is in progress!")

	def read(self, address, length, skip = False):
		if self.connected:
			if not skip:
				if length == 0: raise BaseException("Reading memory requires a length!")
				if not self.validRange(address, length): raise BaseException("Address range not valid")
				if not self.validAccess(address, length, "read"): raise BaseException("Cannot read to address")
			ret = b''
			if length > 0x400:
				for i in range(int(length / 0x400)):
					self.socket.send(b'\x04')
					req = struct.pack(">II", int(address), int(address + 0x400))
					self.socket.send(req)
					if status == b'\xbd': ret += self.socket.recv(length)
					elif status == b'\xb0': ret += b'\x00' * length
					else: raise BaseException("Something went terribly wrong")
					address += 0x400;length -= 0x400
				if length != 0:
					self.socket.send(b'\x04')
					req = struct.pack(">II", int(address), int(address + length))
					self.socket.send(req)
					status = self.socket.recv(1)
					if status == b'\xbd': ret += self.socket.recv(length)
					elif status == b'\xb0': ret += b'\x00' * length
					else: raise BaseException("Something went terribly wrong")
			else:
				self.socket.send(b'\x04')
				req = struct.pack(">II", int(address), int(address + length))
				self.socket.send(req)
				status = self.socket.recv(1)
				if status == b'\xbd': ret += self.socket.recv(length)
				elif status == b'\xb0': ret += b'\x00' * length
				else: raise BaseException("Something went terribly wrong")
			return ret
		else: raise BaseException("No connection is in progress!")

	def kernelWrite(self, address, value, skip = False):
		if self.connected:
			if not skip:
				if not self.validRange(address, 4): raise BaseException("Address range not valid")
				if not self.validAccess(address, 4, "write"): raise BaseException("Cannot write to address")
			self.socket.send(b'\x0B')
			req = struct.pack(">II", int(address), int(value))
			self.socket.send(req)
			return
		else: raise BaseException("No connection is in progress!")

	def kernelRead(self, address, skip = False):
		if self.connected:
			if not skip:
				if not self.validRange(address, 4): raise BaseException("Address range not valid")
				if not self.validAccess(address, 4, "read"): raise BaseException("Cannot read to address")
			self.socket.send(b'\x0C')
			req = struct.pack(">I", int(address))
			self.socket.send(req)
			return struct.unpack(">I", self.socket.recv(4))[0]
		else: raise BaseException("No connection is in progress!")

	def getServerStatus(self):
		if self.connected:
			self.socket.send(b'\x50')
			return int.from_bytes(self.socket.recv(1), "big")
		else: raise BaseException("No connection is in progress!")

	def isConsolePaused(self):
		if self.connected:
			self.socket.send(b'\x84')
			val = int.from_bytes(self.socket.recv(1), "big")
			if val == 1: return True
			else: return False
		else: raise BaseException("No connection is in progress!")

	def pauseConsole(self):
		if self.connected: self.socket.send(b'\x82')
		else: raise BaseException("No connection is in progress!")

	def resumeConsole(self):
		if self.connected: self.socket.send(b'\x83')
		else: raise BaseException("No connection is in progress!")

	def getServerVersion(self):
		if self.connected:
			self.socket.send(b'\x99')
			return self.socket.recv(16).decode("UTF-8").replace('\n', '')
		else: raise BaseException("No connection is in progress!")

	def getOsVersion(self):
		if self.connected:
			self.socket.send(b'\x9A')
			return int.from_bytes(self.socket.recv(4), "big")
		else: raise BaseException("No connection is in progress!")

	def getVersionHash(self):
		if self.connected:
			self.socket.send(b'\xE0')
			return int.from_bytes(self.socket.recv(4), "big")
		else: raise BaseException("No connection is in progress!")

	def getAccountID(self):
		if self.connected:
			self.socket.send(b'\x57')
			return hex(int.from_bytes(self.socket.recv(4), "big")).replace("0x", "")
		else: raise BaseException("No connection is in progress!")

	def getCoreHandlerAddress(self):
		if self.connected:
			self.socket.send(b'\x55')
			return hex(int.from_bytes(self.socket.recv(4), "big"))
		else: raise BaseException("No connection is in progress!")

	def getDataBufferSize(self):
		if self.connected:
			self.socket.send(b'\x51')
			return int.from_bytes(self.socket.recv(4), "big")
		else: raise BaseException("No connection is in progress!")

	def search(self, startAddress, value, length):
		if self.connected:
			self.socket.send(b'\x72')
			req = struct.pack(">III", int(startAddress), int(value), int(length))
			self.socket.send(req)
			return hex(int.from_bytes(self.socket.recv(4), "big"))
		else: raise BaseException("No connection is in progress!")

	def advancedSearch(self, start, length, value, kernel, limit, aligned = 1):
		if self.connected:
			self.socket.send(b'\x73')
			req_val = struct.pack(">I", int(value))
			search_byte_count = len(req_val)
			req = struct.pack(">IIIIII", int(start), int(length), int(kernel), int(limit), int(aligned), int(search_byte_count))
			self.socket.send(req)
			self.socket.send(req_val)
			count = int.from_bytes(self.socket.recv(4), "big") / 4
			foundOffset = []
			for i in range(int(count)):
				foundOffset.append(hex(int.from_bytes(self.socket.recv(4), "big")))
			return foundOffset
		else: raise BaseException("No connection is in progress!")

	def getSymbol(self, rplname, sysname, data = 0):
		if self.connected:
			self.socket.send(b'\x71')
			req = struct.pack('>II', 8, 8 + len(rplname) + 1)
			req += rplname.encode("UTF-8") + b"\x00"
			req += sysname.encode("UTF-8") + b"\x00"
			size = struct.pack(">B", len(req))
			data = struct.pack(">B", data)
			self.socket.send(size)
			self.socket.send(req)
			self.socket.send(data)
			return self.socket.recv(4)
		else: raise BaseException("No connection is in progress!")

	def call(self, address, *args):
		if self.connected:
			arguments = list(args)
			if len(arguments) <= 8:
				while len(arguments) != 8:
					arguments.append(0)
				address = struct.unpack(">I", address)[0]
				req = struct.pack(">I8I", address, *arguments)
				self.socket.send(b'\x70')
				self.socket.send(req)
				return struct.unpack('>I', self.socket.recv(8)[:4])[0]
			else:
				raise BaseException("Too many arguments!")
		else: raise BaseException("No connection is in progress!")

	def getEntryPointAddress(self):
		if self.connected:
			self.socket.send(b'\xB1')
			return hex(int.from_bytes(self.socket.recv(4), "big"))
		else: raise BaseException("No connection is in progress!")

	def runKernelCopyService(self):
		if self.connected: self.socket.send(b'\xCD')
		else: raise BaseException("No connection is in progress!")

	def clearAssembly(self):
		if self.connected: self.socket.send(b'\xE2')
		else: raise BaseException("No connection is in progress!")

	def excecuteAssembly(self, assembly):
		if self.connected:
			self.socket.send(b'\x81')
			req = assembly.encode('UTF-8')
			self.socket.send(req)
		else: raise BaseException("No connection is in progress!")

	def persistAssembly(self, assembly):
		if self.connected:
			self.socket.send(b'\xE1')
			req = assembly.encode('UTF-8')
			self.socket.send(req)
		else: raise BaseException("No connection is in progress!")
