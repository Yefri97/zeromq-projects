import zmq
import json
import math

class WorkerKMean:

	def __init__(self):

		context = zmq.Context()

		self.work = context.socket(zmq.PULL)
		self.work.connect("tcp://localhost:5557")

		# Socket to send messages to
		self.sink = context.socket(zmq.PUSH)
		self.sink.connect("tcp://localhost:5558")

		with open('data/data.txt', 'r') as json_file:
			self.vectors = json.load(json_file)


	def distance(self, vector1, vector2):
		dist = {}
		for key in vector1:
			dist[key] = vector1[key]
		for key in vector2:
			if key in vector1:
				dist[key] = vector2[key] - vector1[key]
			else:
				dist[key] = vector2[key]
		response = 0.0
		for key in dist:
			response += dist[key] * dist[key]
		return response


	def do(self):
		# Process tasks forever
		while True:
			s = self.work.recv_json()

			# Extraigo el vector y los clusters del mensaje
			interval = s['interval']
			clusters = s['clusters']

			# Do the work: Encontrar el cluster mas cercano
			response = [{ 'counter': 0 } for _ in clusters]
			for i in range(interval[0], interval[1] + 1):

				label = 0
				vector = self.vectors[i]
				for i, cluster in enumerate(clusters):
					if self.distance(vector, cluster) < self.distance(vector, clusters[label]):
						label = i

				for dim in vector:
					if dim not in response[label]:
						response[label][dim] = 0.0
					response[label][dim] += vector[dim]

				response[label]['counter'] += 1

			# Send results to sink
			self.sink.send_json({ 'response': response })


def main():
	worker = WorkerKMean()
	print("Worker Listo...", flush = True)
	worker.do()

if __name__ == '__main__':
	main()