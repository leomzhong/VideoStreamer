import pickle
import jsonpickle

def loadMessage(data):
    return jsonpickle.decode(data)

class Message:
    
    def __init__(self, message_type, source_id=-1, flag=True, payload=None):
        self.message_type, self.source_id, self.flag, self.payload = message_type, source_id, flag, payload
    
    def dump(self):
        return jsonpickle.encode(self)
    
    def toString(self):
        result = "message_type:" + self.message_type + "\n"
        result += "source_id:" + str(self.source_id) + "\n"
        result += "flag:" + str(self.flag) + "\n"
        result += "payload:" + str(self.payload) + "\n"
        return result
    
    def getPayLoad(self):
        return self.payload

    def getFlag(self):
        return self.flag

    def getSource(self):
        return self.source_id

    def getMessageType(self):
        return self.message_type
