import pickle

from P2PMessage import Message


def loadNode(encoded):
    return pickle.loads(str(encoded))

class ClientNode(object):
    
    # node info
    host = ""
    server_port = -1
    DHT_port = -1
    nodeId = -1
    
    # current working load
    currentLoad = 0
    
    # TODO: Make the message a separate class
    
    def __init__(self, host, port, nodeId):
        self.host, self.server_port, self.DHT_port, self.nodeId = host, port, port + 1, nodeId
        
    def address(self):
        return (self.host, self.server_port)
    
    def dump(self):
        return pickle.dumps(self)
    
    def binarySearch(self, machine_list, target_nodeId):
        l = 0
        r = len(machine_list) - 1
        while l <= r:
            mid = l + (r - l) / 2
            if loadNode(machine_list[mid]).nodeId == target_nodeId:
                return mid
            elif loadNode(machine_list[mid]).nodeId > target_nodeId:
                r = mid - 1
            else:
                l = mid + 1
        return r
    
    def list_contains_myself(self, machine_list):
        index = self.binarySearch(machine_list, self.nodeId)
        if index == -1 or loadNode(machine_list[index]).nodeId != self.nodeId:
            return False
        else:
            return True
    
    def addToList(self, machine_list):
        index = self.binarySearch(machine_list, self.nodeId)
        if index != -1 and loadNode(machine_list[index]).nodeId == self.nodeId:
            return -1
        else:
            machine_list.insert(index + 1, self.dump())
            return index + 1
    
    def removeFromList(self, machine_list):
        index = self.binarySearch(machine_list, self.nodeId)
        if index != -1 and loadNode(machine_list[index]).nodeId == self.nodeId:
            machine_list.pop(index)    
    
    def _sendmessage(self, message, sock=None, lock=None):
        encoded = message.dump()
        if lock:
            lock.acquire()
            sock.sendto(encoded, self.address())
            lock.release()
        else:
            sock.sendto(encoded, self.address())

    def keep_alive(self, socket=None, source_id=None, lock=None):
        message = Message("keepalive", source_id)
        self._sendmessage(message, socket, lock)
        
    def keep_alive_reply(self, socket=None, source_id=None, lock=None):
        message = Message("keepalive_reply", source_id)
        self._sendmessage(message, socket, lock)
        
    def getload_reply(self, socket=None, source_id=None, lock=None):
        message = Message("getload_reply", source_id, payload = self.currentLoad)
        self._sendmessage(message, socket, lock)
