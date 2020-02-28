# python client.py {action} {data}

import sys
import zmq

context = zmq.Context()

proxy = context.socket(zmq.REQ)
proxy.connect("tcp://localhost:5555") # Proxy

# Chunk's Size: 10MB
ps = 10 * 1024 * 1024

action = sys.argv[1]

if action == 'guardar':

	part = 0
	filepath = sys.argv[2]
	file = open(filepath, 'rb')

	while True:

		part = part + 1
		chunk = file.read(ps)

		if not chunk:
			break

		filename = filepath # TODO
		filename = filename + ".part_" + str(part)

		proxy.send_multipart([b"guardar", filepath.encode(), filename.encode(), str(ps).encode()])
		response = proxy.recv_multipart()
		server = response[0].decode()

		socket = context.socket(zmq.REQ)
		socket.connect("tcp://" + server)
		socket.send_multipart([b"guardar", filename.encode(), chunk])

		ok = socket.recv_multipart()

		print(ok, flush = True)

	file.close()

elif action == 'obtener':
	filename = sys.argv[2]
	proxy.send_multipart([b"listar", filename.encode()])

	partsFiles = proxy.recv_multipart()

	file = open("folder/" + filename, 'wb')
	for part in partsFiles:
		path, server = part.split(";")
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://" + server)
		socket.send_multipart(["obtener", path])
		content = socket.recv_multipart()
		file.write(content)
	file.close()

elif action == 'listar':
	proxy.send_multipart([b"listar"])
	listFiles = proxy.recv_multipart()
	print([file.decode() for file in listFiles])
else:
	print("error")