#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import sys
import zmq
import hashlib

context = zmq.Context()

#  Socket to talk to server
print("Connecting to the server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Chunk's Size: 2MB
ps = 2 * 1024 * 1024

part = 0
filepath = sys.argv[1]
file = open(filepath, 'rb')

while True:

	part = part + 1
	chunk = file.read(ps)

	if not chunk:
		break

	hashing = hashlib.md5(chunk).digest()

	filename = filepath # TODO
	filename = filename + ".part_" + str(part)

	# Enviamos el nombre del archivo, el contenido y un hashing para demostrar integridad
	socket.send_multipart([filename.encode(), chunk, hashing])

	# Recibimos y mostramos el resultado
	result = socket.recv()
	print("Resultado: %s" % result)

file.close()