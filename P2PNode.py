import SocketServer
import json
from pprint import pprint
import socket
import sys
import threading
import time
import traceback

from P2PDHT import P2PDHT
from node import ClientNode
from node import loadNode


nodeIdMax = 1000
recv_buffer_size = 4096
keepalive_period = 5

DEBUG = True

def debug(s):
    global DEBUG
    if DEBUG:
        print("*************DEBUG*************:" + s)

class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request.recv(1024)
            message = json.loads(data)
            message_type = message["message_type"]
            source_id = message["source_id"]
            if message_type == "keepalive":
#                print "We get a pint message from " + str(source_id)
                self.handle_keepalive(self.request, message)
            elif message_type == "keepalive_reply":
#                print "We get a pong message from " + str(source_id)
                pass
            else:
                print "We get a message from " + str(source_id)
                pprint(message)
        except KeyError, ValueError:
            pass
    
    def handle_keepalive(self, client_socket, message):
        # send back pong message or do nothing
        client_host, client_port = self.client_address
        nodeId = message["source_id"]
        replyNode = ClientNode(client_host, client_port, nodeId)
        replyNode.keep_alive_reply(client_socket, self.server.nodeId, self.server.send_lock)

class RequestServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, host_address, handler_cls, nodeId):
        SocketServer.TCPServer.__init__(self, host_address, handler_cls)
        self.send_lock = threading.Lock()
        self.nodeId = nodeId

class P2PNode(object):
    
    # myself
    mynode = None
    
    # map of the movies to local filename
    local_movie_table = {}
    
    # My request server
    request_server = None
    
    # The DHT shared by everyone
    sys_dht = None
    
    # Start procedure:  
    def __init__(self, host, port, nodeId=None, know_host=None, know_port=0):
        debug("host is:" + host)
        debug("port is:" + str(port))
        debug("nodeId is:" + str(nodeId))
        debug("know_host is:" + str(know_host))
        debug("know_host_port is:" + str(know_port))
        
        self.mynode = ClientNode(host, port, nodeId)
        self.request_server = RequestServer((host, port), RequestHandler, nodeId)
        # Check if I am the first node in DHT
        if know_host:
            self.sys_dht = P2PDHT(host, port + 1, know_host, know_port + 1)
        else:
            self.sys_dht = P2PDHT(host, port + 1)
        self.server_thread = threading.Thread(target=self.request_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Add myself to the machine list
        # TODO: Add a distributed lock
        machine_list = []
        if self.sys_dht.has_key("machine_list"):
            machine_list = self.sys_dht.get("machine_list")
        
        if self.mynode.list_contains_myself(machine_list):
            print "We are holding a duplicate nodeId, We need to handle this!!"
        
        my_pos = self.mynode.addToList(machine_list)
        self.sys_dht.put("machine_list", machine_list)
        # TODO: Release the distributed lock
        
        # Generate and start keepalive thread
        self.keepalive_thread = threading.Thread(target=self._KeepAliveThread)
        self.keepalive_thread.daemon = True
        self.keepalive_thread.start()
        
    def _create_socket(self, address):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(address)
        except:
            print "Cannot create socket to " + str(address)
            s = None
        return s
        
    # KeepAlive thread logic    
    def _KeepAliveThread(self):
        global keepalive_period
        global recv_buffer_size
        while True:
            # Get distributed lock
            machine_list = self.sys_dht.get("machine_list")
            if not machine_list:
                print "No machine list? This is really bad!"
                continue
            # Release the distributed lock
            targetNode = self._findKeepAliveNode(self.mynode, machine_list)
            if targetNode:
                keepAliveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_address = targetNode.address()
                    keepAliveSocket.connect(target_address)
                    targetNode.keep_alive(keepAliveSocket, self.mynode.nodeId)
                    recvData = keepAliveSocket.recv(recv_buffer_size)
                    # TODO: No need to check the returnn value?
                except Exception, e:
                    print("Something's wrong with %s. Exception type is %s" % (target_address, e))
                    print "Node " + str(targetNode.nodeId) + " is dead"
                    self._nodeDead(targetNode)
            time.sleep(keepalive_period)
        
    def _nodeDead(self, deadnode):
        # Just delete the node info (including movies) in DHT
        # TODO: For now, just delete the node
        # Get the distributed lock
        machine_list = self.sys_dht.get("machine_list")
        deadnode.removeFromList(machine_list)
        self.sys_dht.put("machine_list", machine_list)
        # Release the distributed lock
    
    def _findKeepAliveNode(self, mynode, machine_list):
        my_pos = mynode.binarySearch(machine_list, mynode.nodeId)
        
        if loadNode(machine_list[my_pos]).nodeId != mynode.nodeId:
            print "KeepAliveThread: Myself is not in the list??? This is really bad"
            return None
        elif len(machine_list) < 2:
            # TODO: Debug info
#            print "I am the only one in the list, no need to keepAlive"
            return None
        elif my_pos == len(machine_list) - 1:
            return loadNode(machine_list[0])
        else:
            return loadNode(machine_list[my_pos + 1])
    
    def _send_message(self, target_nodeId, message):
        # TODO: Get a distributed lock
        machine_list = self.sys_dht.get("machine_list")
        pos = self.mynode.binarySearch(machine_list, target_nodeId)
        targetnode = loadNode(machine_list[pos])
        if targetnode.nodeId != target_nodeId:
            print "There is no such a node with nodeId " + str(target_nodeId)
            return
        s = self._create_socket(targetnode.address())
        targetnode._sendmessage(message, s, self.mynode.nodeId)
            
        
            
        
        
        
        
        