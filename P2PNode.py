import SocketServer
import os
import random
import socket
import threading
import time

from ClientNode import ClientNode
from ClientNode import loadNode
from P2PDHT import P2PDHT
from P2PMessage import loadMessage
from P2PMessage import Message


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
            message = loadMessage(data)
            message_type = message.message_type
            source_id = message.source_id
            if message_type == "keepalive":
#                print "We get a pint message from " + str(source_id)
                self.handle_keepalive(self.request, message)
            else:
                print "We get a message from " + str(source_id)
                print(message.toString())
                if message_type == "getload":
                    self.handle_getload(self.request, message)
        except:
            pass
    
    def handle_keepalive(self, client_socket, message):
        # send back pong message or do nothing
        client_host, client_port = self.client_address
        nodeId = message.source_id
        replyNode = ClientNode(client_host, client_port, nodeId)
        replyNode.keep_alive_reply(client_socket, self.server.nodeId, self.server.send_lock)
        
    def handle_getload(self, client_socket, message):
        client_host, client_port = self.client_address
        nodeId = message.source_id
        replyNode = ClientNode(client_host, client_port, nodeId)
        replyNode.getload_reply(client_socket, self.server.nodeId, self.server.send_lock)

class RequestServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, host_address, handler_cls, nodeId):
        SocketServer.TCPServer.__init__(self, host_address, handler_cls)
        self.send_lock = threading.Lock()
        self.nodeId = nodeId

class P2PNode(object):
    
    # myself
    mynode = None
    
    # map of the movies to local filename
    movietable_lock = None
    local_movie_table = {}
    
    # My request server
    request_server = None
    
    # The DHT shared by everyone
    sys_dht = None
    
    # Start procedure:  
    def __init__(self, host, port, nodeId=None, know_host=None, know_port=0):
        if not nodeId:
            nodeId = self._generate_nodeId()
            
        debug("host is:" + host)
        debug("port is:" + str(port))
        debug("nodeId is:" + str(nodeId))
        debug("know_host is:" + str(know_host))
        debug("know_host_port is:" + str(know_port))
        
        self.movietable_lock = threading.Lock()
        
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
        
        while self.mynode.list_contains_myself(machine_list):
            self.mynode.nodeId = self._generate_nodeId()
            print "We are holding a duplicate nodeId, changing id to " + str(self.mynode.nodeId)
        
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
    
    def _generate_nodeId(self):
        global nodeIdMax
        random.seed(os.urandom(8))
        return int(random.random() * nodeIdMax)
        
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
                    self._removeNode(targetNode)
            time.sleep(keepalive_period)
        
    def _removeNode(self, deadnode):
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
    
    # Return the send_socket back in case outside function need to receive something
    def _send_message(self, target_nodeId, message, send_socket=None):
        targetNode = self._getNodeById(target_nodeId)
        if not targetNode:
            print "There is no such a node with nodeId " + str(target_nodeId)
            return
        if not send_socket:
            send_socket = self._create_socket(targetNode.address())
        targetNode._sendmessage(message, send_socket)
        return send_socket
        
    def _getNodeById(self, target_nodeId):
        # TODO: Get distributed lock
        machine_list = self.sys_dht.get("machine_list")
        pos = self.mynode.binarySearch(machine_list, target_nodeId)
        # TODO: Release distributed lock
        targetnode = loadNode(machine_list[pos])
        if targetnode.nodeId != target_nodeId:
            return None
        else:
            return targetnode
    
    # TODO: Need to hold distributed lock on "movies" to call this function
    def _getMovieTable(self):
        movie_table = self.sys_dht.get("movies")
        if not movie_table:
            movie_table = {}
            self.sys_dht.put("movies", movie_table)
        return movie_table

    # TODO: Need to hold distributed lock on "movies" to call this function
    def _updateMovieTable(self, new_table):
        self.sys_dht.put("movies", new_table)
        
    # TODO: Need to hold distributed lock on nodename to call this function
    def _getMovieListOnNode(self, nodeId):
        nodename = "nodename" + str(nodeId)
        movie_list = self.sys_dht.get(nodename)
        if not movie_list:
            movie_list = []
        return movie_list
    
    # TODO: Need to hold distributed lock on movie_name to call this function
    def _addNodeToMovie(self, movie_name, new_node):
        movie_table = self._getMovieTable()
        node_list = movie_table.get(movie_name)
        if not node_list:
            node_list = []
        node_list.append(new_node.dump())
        movie_table[movie_name] = node_list
        self._updateMovieTable(movie_table)
    
    # TODO: Need to hold distributed lock on movie_name to call this function
    def _removeNodeFromMovie(self, movie_name, node):
        movie_table = self._getMovieTable()
        if not movie_table.has_key(movie_name):
            print "_removeNodeFromMovie: there is no movie " + movie_name
            return
        node_list = movie_table.get(movie_name)
        node.removeFromList(node_list)
        if len(node_list) == 0:
            del movie_table[movie_name]
        else:
            movie_table[movie_name] = node_list
        self._updateMovieTable(movie_table)
    
    # TODO: Need to hold distributed lock on movie_name to call this function
    def _addMovieToNode(self, movie_name):
        nodename = self.mynode.getname()
        movie_list = self.sys_dht.get(nodename)
        if not movie_list:
            movie_list = []
        movie_list.append(movie_name)
        self.sys_dht.put(self.mynode.getname(), movie_list)
    
    # TODO: Need to hold distributed lock on movie_name to call this function
    def _removeMovieFromNode(self, movie_name):
        nodename = self.mynode.getname()
        movie_list = self.sys_dht.get(nodename)
        if not movie_list:
            print "_remoeMovieFromNode: there is no movie list for node: " + self.mynode.getname()
        try:
            movie_list.remove(movie_name)
        except:
            print "_removeMovieFromNode: You don't have this movie"
        self.sys_dht.put(movie_name, movie_list)
    
    # Public APIs
    
    # Myself leave the system
    def leave(self):
        # It's the same as myself is dead
        self._removeNode(self.mynode)
        
    def uploadMovie(self, movie_name, local_filename):
        self.movietable_lock.acquire()
        if self.local_movie_table.has_key(movie_name):
            print "You already has movie " + movie_name + " uploaded"
            return False
        
        self.local_movie_table[movie_name] = local_filename
        self.movietable_lock.release()
        # TODO: Need to hold distributed lock on "movies" and movie_name
        self._addMovieToNode(movie_name)
        self._addNodeToMovie(movie_name, self.mynode)
        return True
        
    def removeMovie(self, movie_name):
        self.movietable_lock.acquire()
        if not self.local_movie_table.has_key(movie_name):
            print "You don't have " + movie_name + " in your movie table"
            return False
        # TODO: Need to hold distributed lock on "movies" and movie_name
        del self.local_movie_table[movie_name]
        self.movietable_lock.release()
        self._removeNodeFromMovie(movie_name, self.mynode)
        self._removeMovieFromNode(movie_name)
        return True

    def getMovieList(self):
        # TODO: Need to hold the distributed lock on "movies"
        movie_table = self._getMovieTable()
        return movie_table.keys()

    def getNodeListOfMovie(self, movie_name):
        # TODO: Need to hold the distributed lock on "movies"
        movie_table = self._getMovieTable()
        node_list = []
        if movie_table.has_key(movie_name):
            node_list = movie_table.get(movie_name)
        result = []
        for node in node_list:
            tmpNode = loadNode(node)
            result.append(str(tmpNode.nodeId))
        return result
    
    def getMoviesOnANode(self, nodeId):
        # TODO: Need to hold the distributed lock on nodename
        return self._getMovieListOnNode(nodeId)
        
    def getNodeLoad(self, target_nodeId):
        message = Message("getload", self.mynode.nodeId)
        # TODO: The node may already dead here
        send_socket = self._send_message(target_nodeId, message)
        replyData = send_socket.recv(1024)
        replyMessage = loadMessage(replyData)
        print(replyMessage.toString())
        return int(replyMessage.payload)
        
        
        
            
        
            
        
        
        
        
        