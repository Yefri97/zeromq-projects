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

filepath = sys.argv[1]
file = open(filepath, 'rb')
content = file.read()
file.close();

hashing = hashlib.md5(content).digest()

# Enviamos el nombre del archivo, el contenido y un hashing para demostrar integridad
socket.send_multipart([filepath.encode(), content, hashing])

# Recibimos y mostramos el resultado
result = socket.recv()
print("Resultado: %s" % result)