import zmq
import math

def distancia(vector1, vector2):
	dist = 0.0
	for (x1, x2) in zip(vector1, vector2):
		dist += (x1 - x2) * (x1 - x2)
	return math.sqrt(dist)

context = zmq.Context()

work = context.socket(zmq.PULL)
work.connect("tcp://localhost:5557")

# Socket to send messages to
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

# Process tasks forever
while True:
	s = work.recv_json()

	# Extraigo el vector y los clusters del mensaje
	vectores = s['vectores']
	clusters = s['clusters']

	# Do the work: Encontrar el cluster mas cercano
	response = []
	for vector in vectores:
		cr_near = -1
		for idc in range(len(clusters)):
			if cr_near == -1 or distancia(vector, clusters[idc]) < distancia(vector, clusters[cr_near]):
				cr_near = idc
		response.append([vector, cr_near])

	# print(vector, cr_near, flush = True)

	# Send results to sink
	sink.send_json({ 'response': response })
