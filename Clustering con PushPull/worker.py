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

		with open('data/ranks.txt', 'r') as json_file:
			self.vectors = json.load(json_file)


	def distance_to_cluster(self, vector, id_cluster):
		dist = self.values_clusters[id_cluster]
		for key in vector:
			if key in self.clusters[id_cluster]:
				dist -= self.clusters[id_cluster][key] ** 2
				dist += (vector[key] - self.clusters[id_cluster][key]) ** 2
			else:
				dist += vector[key] ** 2
		if dist < 0:
			dist = 0.0
		return dist


	def do(self):
		# Process tasks forever
		while True:
			s = self.work.recv_json()

			# Extraigo el vector y los clusters del mensaje
			interval = s['interval']
			self.clusters = s['clusters']
			self.values_clusters = s['values_clusters']

			# Do the work: Encontrar el cluster mas cercano
			response = [{ 'counter': 0 } for _ in self.clusters]
			for i in range(interval[0], interval[1] + 1):
				vector = self.vectors[i]
				label, best = (-1, -1)
				for j in range(len(self.clusters)):
					dist = self.distance_to_cluster(vector, j)
					if label == -1 or dist < best:
						label = j
						best = dist

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