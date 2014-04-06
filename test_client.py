import sys

from P2PNode import P2PNode
from P2PMessage import Message

def main(sys_args):
    if not sys_args or len(sys_args) < 2:
        return
    hostname = sys_args[0]
    hostport = int(sys_args[1])
    knowhost = None
    knowport = 0
    if len(sys_args) > 2:
        knowhost = sys_args[2]
        knowport = int(sys_args[3])
    p2pnode = P2PNode(hostname, hostport, know_host=knowhost, know_port = knowport)
    
    while True:
        command = raw_input("enter command:")
        if command == "message":
            nodeId = int(raw_input("enter nodeId:"))
            message_type = raw_input("enter message_type")
            s = raw_input("enter the message:")
        else:
            message_type = command
            s = raw_input("enter arguments:")
        
        # Testing getload function
        if message_type == "getload":
            p2pnode.getNodeLoad(nodeId)
        # Testing upload movie
        elif message_type == "upload":
            words = s.split()
            p2pnode.uploadMovie(words[0], words[1])
        # Testing remove movie
        elif message_type == "remove":
            p2pnode.removeMovie(s)
        # Testing get movie list:
        elif message_type == "getmovies":
            print("movies:" + "\t".join(p2pnode.getMovieList()))
        # Testing get node list of a movie
        elif message_type == "getmovienode":
            print("nodes for movie " + s + ":" + "\t".join(p2pnode.getNodeListOfMovie(s)))
        elif message_type == "getnodemovie":
            print("movies on mynode is:" + "\t".join(p2pnode.getMoviesOnANode(p2pnode.mynode.nodeId)))
        elif command == "message":
            message = Message(message_type, p2pnode.mynode.nodeId, payload = s)
            p2pnode._send_message(nodeId, message)

if __name__ == "__main__":
    main(sys.argv[1:])