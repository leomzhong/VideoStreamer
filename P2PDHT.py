import threading

from pydht.pydht import DHT


class P2PDHT:
    
    def __init__(self, host, port, know_host=None, know_port=0):
        if know_host:
            self.my_dht = DHT(host, port, boot_host = know_host, boot_port = know_port)
        else:
            self.my_dht = DHT(host, port)
        self.dht_lock = threading.Lock()
        
    def get(self, key):
        self.dht_lock.acquire()
        result = None
        try:
            result = self.my_dht[key]
        except:
            pass
        self.dht_lock.release()
        if not result:
            return None
        else:
            return result
    
    def put(self, key, value):
        self.dht_lock.acquire()
        try:
            self.my_dht[key] = value
        except:
            pass
        self.dht_lock.release()
        
    def has_key(self, key):
        self.dht_lock.acquire()
        result = None
        try:
            result = self.my_dht[key]
        except:
            pass
        self.dht_lock.release()
        if not result:
            return False
        else:
            return True
        
    def remove(self, key):
        if not self.has_key(key):
            return
        else:
            self.dht_lock.acquire()
            self.my_dht[key] = None
            self.dht_lock.release()
            
        