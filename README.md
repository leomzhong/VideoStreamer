VideoStreamer
=============

To run test_client
1. Run a node with Command: python test_client.py localhost 30000 1
2. Run another node with Command: python test_client.py localhost 30002 2 localhost 30000


You can enter nodeId and message to play with it
Note: Each node will use two port(for the first node is 30000 and 30000 + 1). So do not choose consecutive port for different node on the same machine
