import zmq
import sys

ip, port = (sys.argv[1], sys.argv[2])

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://{}:{}".format(ip, port))

socket.send(b"get")
idr = socket.recv()

print(idr)