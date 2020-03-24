# python server.py {my_address} {ring_address}

import os
import sys
import zmq
import math
from random import random

max_number = 10000000

# info_server = (id, address, prev_address)
# id = [1..max_number]
# addres = "{ip}:{port}"
# prev = "{ip}:{port}"

# Registrar

def encode(l):
	return [x.encode() for x in l]

def decode(l):
	return [x.decode() for x in l]

def get_info_serve(address):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://{}".format(address))
	socket.send_multipart(encode(["info"]))
	return decode(socket.recv_multipart())

def get_responsable(idr, ring_address):
	while True:
		info_current = get_info_serve(ring_address)
		info_prev = get_info_serve(info_current[2])
		range_current = [int(info_prev[0]), int(info_current[0]) - 1]
		if range_current[1] == -1:
			range_current[1] = max_number
		if range_current[0] <= idr and idr <= range_current[1]:
			return info_current
		ring_address = info_prev[1]

def update_prev(address, new_prev_address):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://{}".format(address))
	socket.send_multipart(encode(["update", new_prev_address]))
	message = decode(socket.recv_multipart())
	print(message[0], flush = True)

def get_list(address):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://" + address)
	socket.send_multipart(encode(["list"]))
	return decode(socket.recv_multipart())

def get_hash(folder, chunk_hash, address):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://" + address)
	socket.send_multipart(encode(["download", chunk_hash]))
	content = socket.recv_multipart()
	port = address.split(":")[1]
	print(folder + "/" + chunk_hash, flush = True)
	file = open(folder + "/" + chunk_hash, 'wb')
	file.write(content[0])
	file.close()

my_address, ring_address = (sys.argv[1], sys.argv[2])

list_hashes = list()
list_hashes.append("list_hashes")

address = my_address
ip, port = address.split(":")

folder = "folder-" + port

if not os.path.isdir(folder):
	os.mkdir(folder)

if ring_address == "-1":
	idr = 0
	prev = my_address
else:
	idr = math.floor(random() * max_number)
	responsable = get_responsable(idr, ring_address)
	prev = responsable[2]

	for chunk_hash in get_list(responsable[1]):
		if chunk_hash == 'list_hashes':
			continue
		info_prev = get_info_serve(prev)
		my_range = [int(info_prev[0]), idr - 1]
		if my_range[0] <= int(chunk_hash) and int(chunk_hash) <= my_range[1]:
			get_hash(folder, chunk_hash, responsable[1])

	update_prev(responsable[1], my_address)

print("El id asignado a este este servidor es: {}".format(idr), flush = True)
print("Y la direccion de su anterior es: {}".format(prev), flush = True)

# Servidor que hace del parte del anillo

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:{}".format(port))

# print("Servidor corriendo en el puerto: {}".format(port), flush = True)

while True:

	message = socket.recv_multipart()
	action = message[0].decode()

	if action == 'info':

		socket.send_multipart(encode([str(idr), address, prev]))

	elif action == 'update':

		new_prev_address = message[1].decode()
		prev = new_prev_address

		socket.send_multipart(encode(["El nuevo prev de {} es {}".format(address, prev)]))

	elif action == 'upload':

		filename, content = (message[1].decode(), message[2])

		file = open(folder + "/" + filename, 'wb')
		file.write(content)
		file.close()

		socket.send_multipart(encode(["Trozo Guardado"]))

		list_hashes.append(filename)

	elif action == 'download':

		filename = message[1].decode()

		file = open(folder + "/" + filename, 'rb')
		content = file.read()
		socket.send_multipart([content])

	elif action == 'list':

		socket.send_multipart(encode(list_hashes))

	else:

		socket.send_multipart(encode(["Acción no permitida"]))
		print("Acción no permitida")