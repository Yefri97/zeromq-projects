#Client

import sys
import zmq
import os
import hashlib

ps = 10 * 1024 * 1024
max_number = 10000000

def encode(l):
	return [x.encode() for x in l]

def decode(l):
	return [x.decode() for x in l]

def hash(filename):
	sha1 = hashlib.sha1()
	with open (filename, 'rb') as f:
		while True:
			data = f.read(ps)
			if not data:
				break
			sha1.update(data)
	return sha1.hexdigest()

def new_txt(nombre):
	file = open(nombre, 'rb')
	file_txt = open(nombre + ".txt", "w")
	while True:
		chunk = file.read(ps)
		if not chunk:
			break
		chunk_hash = hashlib.sha1(chunk)
		file_txt.write(chunk_hash + os.linesep)
	file.close()
	file_txt.close()
	return hash(nombre)

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

def reduce(big_number):
	return int(big_number) % max_number

ring_address, action = (sys.argv[1], sys.argv[2])

if action == 'upload':

	file2upload = sys.argv[3]
	file_txt = new_txt(file2upload)
	print("Totient generado en " + file_txt)

	file = open(file2upload, 'rb')
	
	while True:

		chunk = file.read(ps)

		if not chunk:
			break

		# Obtiene al responsable
		chunk_hash = hashlib.sha1(chunk)
		responsable = get_responsable(reduce(chunk_hash), ring_address)

		# Le envia el chunk al responsable
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://" + responsable[1])
		socket.send_multipart([b'upload', chunk])

	file.close()

elif action == 'download':

	filename = sys.argv[3] # Path from the .txt

else:
	print("error")