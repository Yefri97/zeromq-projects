import time
import zmq
import json
import math
import random
from matplotlib import pyplot as plt


MAX_NUMBER = 1000
COLORS = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']


def generar_vector_aleatorio(dimension):
	coor = random.randint(0, 1)
	return {str(i): random.randint(0, MAX_NUMBER) for i in range(dimension)}


class FanKMeans:

	def __init__(self, max_iterations = 50, tolerance = 0.00001):

		self.max_iterations = max_iterations
		self.tolerance = tolerance

		# Conecta con los Workers y el Sink
		context = zmq.Context()

		# socket with workers
		self.workers = context.socket(zmq.PUSH)
		self.workers.bind("tcp://*:5557")

		# socket with sink
		self.sink_push = context.socket(zmq.PUSH)
		self.sink_push.connect("tcp://localhost:5558")

		self.sink_pull = context.socket(zmq.PULL)
		self.sink_pull.bind("tcp://*:5556")


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


	def train(self, num_vectors, num_dimensions, num_clusters):

		self.clusters = [generar_vector_aleatorio(num_dimensions) for _ in range(num_clusters)]
		
		num_iterations = 0
		while num_iterations < self.max_iterations:
			num_iterations += 1

			sqrt = math.floor(math.sqrt(num_vectors))

			it = 0
			tasks = []
			while it < num_vectors:
				tasks.append([it, min(it + sqrt, num_vectors) - 1])
				it += sqrt

			self.sink_push.send_json({
				'n_tasks': len(tasks),
				'n_clusters': num_clusters
			})

			for task in tasks:
				self.workers.send_json({
					'interval': task,
					'clusters': self.clusters,
				})
			
			new_clusters = self.sink_pull.recv_json()['response']

			diff = 0.0
			for (c1, c2) in zip(self.clusters, new_clusters):
				diff += math.sqrt(self.distance(c1, c2))

			if diff < self.tolerance:
				break

			self.clusters = new_clusters

		print("Numero de iteraciones", num_iterations)


	def predict(self, vector):
		label = 0
		for i, cluster in enumerate(self.clusters):
			if self.distance(vector, cluster) < self.distance(vector, self.clusters[label]):
				label = i
		return label


def main():

	num_vectors = 160000
	num_dimensions = 2
	num_clusters = 5

	random.seed()
	data = [generar_vector_aleatorio(num_dimensions) for _ in range(num_vectors)]

	with open('data/data.txt', 'w') as f:
		f.write(json.dumps(data))

	kmeans = FanKMeans()
	print("Presione Enter cuando los trabajadores esten listos...", flush = True)
	_ = input()
	print("Iniciando Clasificación", flush = True)

	time_start = time.time()
	kmeans.train(num_vectors, num_dimensions, num_clusters)
	time_final = time.time()
	print("Tiempo de Entrenamiento: ", time_final - time_start)

	# Plot the results
	"""for i, cluster in enumerate(kmeans.clusters):
		plt.scatter(cluster.get('0', 0), cluster.get('1', 0), s = 300, c = COLORS[i])

	for vector in data:
		label = kmeans.predict(vector)
		plt.scatter(vector.get('0', 0), vector.get('1', 0), c = COLORS[label])

	plt.show()"""


if __name__ == "__main__":
	main()