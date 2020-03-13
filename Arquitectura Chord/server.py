# python server.py {myserver} {myport} {server2} {port2}

import sys
import zmq
import math
from random import random

my_ip, my_port, ring_ip, ring_port = (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# my_ip, my_port = (sys.argv[1], sys.argv[2])

idr = math.floor(random() * 1000)
print("El id de este servidor es: {}".format(idr))

context = zmq.Context()

ring = context.socket(zqm.REQ)
ring.connect("tcp://{}:{}".format(ring_ip, ring_port))

while True:
	ring.send_multipart()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:{}".format(my_port))


while True:

	message = socket.recv()
	socket.send(str(idr).encode())