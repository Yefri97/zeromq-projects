#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import zmq
import hashlib

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	#  Wait for next request from client
	filename, content, hashing1 = socket.recv_multipart()
	print("Received request")

	hashing2 = hashlib.md5(content).digest()

	if hashing1 == hashing2:

		file = open("folder/" + filename.decode(), 'wb')
		file.write(content)
		file.close()

		socket.send(b"Exitoso")

	else:

		socket.send(b"Error")