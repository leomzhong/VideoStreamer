import sys

from P2PNode import P2PNode

def main(sys_args):
    hostname = sys_args[0]
    hostport = int(sys_args[1])
    nodeid = int(sys_args[2])
    knowhost = None
    knowport = 0
    if len(sys_args) > 3:
        knowhost = sys_args[3]
        knowport = int(sys_args[4])
    p2pnode = P2PNode(hostname, hostport, nodeid, knowhost, knowport)
    while True:
        nodeId = int(raw_input("enter nodeId:"))
        s = raw_input("enter the message")
        message = {
            "message_type": "shell_command"
        }
        message["content"] = s
        p2pnode._send_message(nodeId, message)

if __name__ == "__main__":
    main(sys.argv[1:])