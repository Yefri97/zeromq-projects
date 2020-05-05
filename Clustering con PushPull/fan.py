import time
import zmq
import json
import math
import random
from matplotlib import pyplot as plt


MAX_NUMBER = 1000
COLORS = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']


def generar_vector_aleatorio(dimension):
	return {str(i): random.randint(0, MAX_NUMBER) for i in range(dimension)}


class FanKMeans:

	def __init__(self, max_iterations = 60, tolerance = 0.00001):

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
			time_start = time.time()
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

			self.values_clusters = []
			for cluster in self.clusters:
				value = 0
				for key in cluster:
					value += cluster[key] ** 2
				self.values_clusters.append(value)

			for task in tasks:
				self.workers.send_json({
					'interval': task,
					'clusters': self.clusters,
					'values_clusters': self.values_clusters,
				})
			
			new_clusters = self.sink_pull.recv_json()['response']

			diff = 0.0
			for (c1, c2) in zip(self.clusters, new_clusters):
				diff += math.sqrt(self.distance(c1, c2))

			if diff < self.tolerance:
				break

			self.clusters = new_clusters

			time_final = time.time()
			print("Iteracion:", num_iterations, ", Tiempo:", time_final - time_start, flush = True)

		print("Numero de iteraciones", num_iterations)


	def predict(self, vector):
		label, best = (-1, -1)
		for i in range(len(self.clusters)):
			dist = self.distance_to_cluster(vector, i)
			if label == -1 or dist < best:
				label = i
				best = dist
		return (label, best)


def main(debug = 1):

	if debug:
		num_vectors = 100
		num_dimensions = 2
		max_num_clusters = 3
		# random.seed()
		data = [generar_vector_aleatorio(num_dimensions) for _ in range(num_vectors)]
		with open('data/ranks.txt', 'w') as f:
			f.write(json.dumps(data))
	else:
		num_vectors = 470758
		num_dimensions = 4499
		max_num_clusters = 2
		with open('data/ranks.txt', 'r') as json_file:
			data = json.load(json_file)
	
	kmeans = FanKMeans()
	print("Presione Enter cuando los trabajadores esten listos...", flush = True)
	_ = input()
	print("Iniciando Clasificacion", flush = True)

	for num_clusters in range(max_num_clusters, max_num_clusters+1):
		print("K = ", num_clusters)
		time_start = time.time()
		kmeans.train(num_vectors, num_dimensions, num_clusters)
		time_final = time.time()
		print("Tiempo de Entrenamiento: ", time_final - time_start)

		inertia = 0.0
		for vector in data:
			(label, dist) = kmeans.predict(vector)
			inertia += dist
		print("Inercia: ", math.sqrt(inertia), flush = True)

		if debug:
			for i, cluster in enumerate(kmeans.clusters):
				plt.scatter(cluster.get('0', 0), cluster.get('1', 0), s = 300, c = COLORS[i])

			for vector in data:
				label = kmeans.predict(vector)[0]
				plt.scatter(vector.get('0', 0), vector.get('1', 0), c = COLORS[label])
		"""else:
			for i, cluster in enumerate(kmeans.clusters):
				plt.scatter(num_clusters, inertia, c = COLORS[0])"""

	#plt.show()

if __name__ == "__main__":
	main(debug = 0)