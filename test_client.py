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
        nodeId = int(raw_input("enter nodeId:"))
        s = raw_input("enter the message")
        message = Message("shell_message", p2pnode.mynode.nodeId, payload = s)
        p2pnode._send_message(nodeId, message)

if __name__ == "__main__":
    main(sys.argv[1:])