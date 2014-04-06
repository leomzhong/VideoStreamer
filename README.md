VideoStreamer
=============

To run test_client:
	1. Run a node with Command: 
		python test_client.py localhost 30000
	2. Run another node with Command: 
		python test_client.py localhost 30002 localhost 30000

Note: Each node will use two port(for the first node is 30000 and 30000 + 1). So do not choose consecutive port for different node on the same machine

USAGE:
1. send message(command: message)
2. upload movie:
	command: upload
	arguments: movie_name local_file_name

3. remove movie:
	command: remove
	arguments: movie_name

4. get movie list:
	command: getmovies
	arguments: [not needed]

5. get list of node of a movie:
	command: getmovienode
	arguments: movie_name

6. get list of movie on local node:
	command: getnodemovie
	arguments: [not needed]
