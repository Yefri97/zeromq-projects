#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
	#  Wait for next request from client
	formula = socket.recv_string()
	print("Received request: %s" % formula)

	a = ord(formula[0]) - ord('0')
	b = ord(formula[4]) - ord('0')

	if formula[2] == '+':
		socket.send_string(str(a + b))
	elif formula[2] == '*':
		socket.send_string(str(a * b))
	elif formula[2] == '-':
		socket.send_string(str(a - b))
	elif formula[2] == '/':
		socket.send_string(str(a / b))
	else:
		socket.send_string("end")
		break