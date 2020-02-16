#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Enviamos la formula que va a ser procesada
# Ejemplos: 3 + 5, 5 * 6, 3 / 2, 9 - 8
formula = input()

# Enviamos la formula por el socket
socket.send_string(formula)

# Recibimos y mostramos el resultado
result = socket.recv_string()
print("%s = %s" % (formula, result))