# python server.py {myserver} {myport} {server2} {port2}

import sys
import zmq
import math
from random import random

my_address, ring_address = (sys.argv[1], sys.argv[2])

# info_server = (id, address, prev_address)

# id = [1..1000]
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
			range_current[1] = 1000
		if range_current[0] <= idr and idr <= range_current[1]:
			return info_current
		ring_address = info_prev[1]

def update_prev(address, new_prev_address):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://{}".format(address))
	socket.send_multipart(encode(["update", new_prev_address]))
	message = decode(socket.recv_multipart())
	print(message[0])

address = my_address
if ring_address == "-1":
	idr = 0
	prev = my_address
else:
	idr = math.floor(random() * 1000)
	responsable = get_responsable(idr, ring_address)
	prev = responsable[2]
	update_prev(responsable[1], my_address)

print("El id asignado a este este servidor es: {}".format(idr))
print("Y la direccion de su anterior es: {}".format(prev))

# Servidor que hace del parte del anillo

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:{}".format(address.split(":")[1]))

# print("Servidor corriendo en el puerto: {}".format(address.split(":")[1]))

while True:

	message = decode(socket.recv_multipart())
	action = message[0]

	if action == 'info':

		socket.send_multipart(encode([str(idr), address, prev]))

	elif action == 'update':

		new_prev_address = message[1]
		prev = new_prev_address

		socket.send_multipart(encode(["El nuevo prev de {} es {}".format(address, prev)]))
