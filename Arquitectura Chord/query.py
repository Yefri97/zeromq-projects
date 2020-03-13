import zmq
import sys

address = sys.argv[1]

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://{}".format(address))

def encode(l):
	return [x.encode() for x in l]

def decode(l):
	return [x.decode() for x in l]

socket.send_multipart(encode(["info"]))
info = decode(socket.recv_multipart())

print(info)
