# python server.py {ip} {port} {capacity}
# python server.py localhost 5551 1000

import os
import sys
import zmq

ip, port, capacity = (sys.argv[1], sys.argv[2], sys.argv[3])

context = zmq.Context()

proxy = context.socket(zmq.REQ)
proxy.connect("tcp://localhost:5555") # Proxy
proxy.send_multipart([b"registrar", ip.encode(), port.encode(), capacity.encode()])
ok = proxy.recv_multipart()
print(ok[0].decode(), flush = True)

socket = context.socket(zmq.REP)
socket.bind("tcp://*:{}".format(port))

folder = ip + "-" + port
os.mkdir(folder)

while True:

	message = socket.recv_multipart()
	action = message[0].decode()

	if action == 'guardar':

		filename, content = message[1], message[2]

		file = open(folder + "/" + filename.decode(), 'wb')
		file.write(content)
		file.close()

		socket.send_multipart([b"Trozo Guardado"])

	elif action == 'obtener':

		filename = message[1]

		file = open(folder + "/" + filename.decode(), 'rb')
		content = file.read()
		socket.send_multipart([content])

	else:

		socket.send_multipart([b"error"])