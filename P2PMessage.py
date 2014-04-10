import pickle

def loadMessage(data):
    return pickle.loads(str(data))

class Message:
    
    def __init__(self, message_type, source_id=-1, flag=True, payload=None):
        self.message_type, self.source_id, self.flag, self.payload = message_type, source_id, flag, payload
    
    def dump(self):
        return pickle.dumps(self)
    
    def toString(self):
        result = "message_type:" + self.message_type + "\n"
        result += "source_id:" + str(self.source_id) + "\n"
        result += "flag:" + str(self.flag) + "\n"
        result += "payload:" + str(self.payload) + "\n"
        return result 
