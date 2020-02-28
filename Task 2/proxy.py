# python proxy.py


import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
print("Proxy Iniciado", flush = True)

iterator = 0
nServers = 0
servers = list()
available = list()
registry = {}

while True:

	message = socket.recv_multipart()

	action = message[0].decode()

	if action == 'registrar':

		ip, port, capacity = (message[1], message[2], message[3])

		servers.append(ip + b":" + port)
		available.append(int(capacity.decode()))

		socket.send_multipart([b"Servidor Registrado"])

		nServers = nServers + 1

		print("Servidor Registrado", flush = True)

	elif action == 'guardar':
		
		filename, part, weight = (message[1], message[2], message[3])

		filename = filename.decode()
		if filename not in registry:
			registry[filename] = list()
		registry[filename].append([part + b";" + servers[iterator]])

		available[iterator] -= int(weight.decode())

		socket.send_multipart([servers[iterator]])

		iterator = (iterator + 1) % nServers

	elif action == 'obtener':

		filename = message[1]

		socket.send_multipart([data.encode() for data in registry[filename]])

	elif action == 'listar':

		socket.send_multipart([file.encode() for file in registry])

	else:

		socket.send_multipart([b"error"])
		print("Acción no Valida")
