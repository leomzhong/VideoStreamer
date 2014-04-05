from pydht import DHT
from multiprocessing import Lock

class DHT842:
	def __init__(self, ip, port, master_ip = None, master_port = None):
		if(master_ip is None and master_port is None):
			self.dht_global = DHT(ip, port)
			self.lock = Lock()
		elif(master_ip is not None and master_port is not None):
			self.dht_global = DHT(ip, port, boot_host = master_ip, boot_port = master_port)
			self.lock = Lock()
		else:
			print 'Missing master ip or master port'
			return -1			

	def has_key(self, key_value):
		with self.lock:
			try:
				self.dht_global[key_value]
			except KeyError:
				return 0
		return 1
	#return None when there is no this key-value pair exists in the DHT
	def get(self, key_value):
		if self.has_key(key_value) == 0:
			return None
		else:
			return self.dht_global[key_value]
	def put(self, key, value):
		with self.lock:
			self.dht_global[key] = value
	#return 0 when there is no this key-value pair exists in the DHT
	def remove(self, key_value):
		if self.has_key(key_value) == 0:
			return 0
		with self.lock:
			self.dht_global[key_value] = None
			return 1
