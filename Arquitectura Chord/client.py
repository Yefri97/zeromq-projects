#Client

import sys
import zmq
import os
import hashlib

ps = 10 * 1024 * 1024
max_number = 1000000000

def size(file):
	sizeFile = os.stat(file).st_size
	return sizeFile

def porc(x, y):
	return (x / y) * 100

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
	nombre_txt = hash(nombre)[:8]
	file = open(nombre, 'rb')
	file_txt = open(nombre_txt + ".txt", "w")
	file_txt.write(nombre + '\n')
	while True:
		chunk = file.read(ps)
		if not chunk:
			break
		chunk_hash = hashlib.sha1(chunk).hexdigest()
		file_txt.write(str(reduce(chunk_hash)) + '\n')
	file.close()
	file_txt.close()
	return nombre_txt

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
	return int(big_number, 16) % max_number

ring_address, action = (sys.argv[1], sys.argv[2])

if action == 'upload':

	file2upload = sys.argv[3]
	file_txt = new_txt(file2upload)
	tamaño = size(file2upload)
	toUpload = 0
	file = open(file2upload, 'rb')
	porcentaje = 0
	while True:
		toUpload = toUpload + ps
		porcentaje = porcentaje + porc(ps,tamaño)
		chunk = file.read(ps)
		if toUpload < tamaño:
			print("Completado: " + str(porcentaje)  + "% de 100%")
		if not chunk:
			print("Completado: 100% de 100%")
			break

		# Obtiene al responsable
		chunk_hash = hashlib.sha1(chunk).hexdigest()
		responsable = get_responsable(reduce(chunk_hash), ring_address)

		# Le envia el chunk al responsable
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://" + responsable[1])
		socket.send_multipart([b'upload', str(reduce(chunk_hash)).encode(), chunk])

	print("Archivo txt generado correctamente en " + file_txt)
	file.close()

elif action == 'download':

	nametxt = sys.argv[3] # Path from the .txt
	#file_txt = new_txt(file2upload)
	#print("Totient generado en " + file_txt)
	print("Iniciando descarga...")
	file_txt = open(nametxt, "r")


	filename = file_txt.readline().strip()
	tamaño = size(filename)
	file = open("downloads/" + filename, 'wb')
	toDownload = 0
	porcentaje = 0
	print("Completado: " + str(porcentaje)  + "% de 100%")
	chunk_hash = file_txt.readline().strip()
	while chunk_hash:
		responsable = get_responsable(int(chunk_hash), ring_address)
		toDownload = toDownload + ps
		porcentaje = porcentaje + porc(ps, tamaño)
		print("Descargando : " + str(min(porcentaje, 100.0)) + "% de 100%")
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://" + responsable[1])
		socket.send_multipart(encode(["download", chunk_hash]))

		content = socket.recv_multipart()
		file.write(content[0])
		chunk_hash = file_txt.readline().strip()

	print("Descargado correctamente : " + nametxt)
	file_txt.close()
	file.close()

else:
	print("error")
