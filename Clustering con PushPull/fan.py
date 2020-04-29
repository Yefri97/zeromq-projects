import time
import zmq
import math
import random
from matplotlib import pyplot as plt

EPS = 0.000001
MAX_NUMBER = 10000
COLORS = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']

def generar_vector_aleatorio(dimension):
	coor = random.randint(0, 1)
	return {str(i): random.randint(0, MAX_NUMBER) for i in range(dimension)}


def generar_clusters_aleatorios(num_clusters, dim_vectores):
	return [generar_vector_aleatorio(dim_vectores) for _ in range(num_clusters)]


def centroide(vectores, dim):
	response = {str(i): 0 for i in range(dim)}
	for vector in vectores:
		for key in vector:
			response[key] += vector[key] * 1.0 / len(vectores)
	return response


def find_near(vectores, clusters):

	sqrt = math.floor(math.sqrt(len(vectores)))

	sink_push.send_json({
		'n_tasks': sqrt
	})

	it = 0
	while it < len(vectores):
		work = []
		while it < len(vectores) and len(work) < sqrt:
			work.append(vectores[it][0])
			it += 1
		workers.send_json({
			'vectores': work,
			'clusters': clusters,
		})

	new_vectores = sink_pull.recv_json()['response']

	return new_vectores


def distancia(vector1, vector2):
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


def kmean(vectores, dim_vectores, num_clusters):
	
	vectores = [[vector, -1] for vector in vectores]
	clusters = generar_clusters_aleatorios(num_clusters, dim_vectores)

	num_iteraciones = 0
	while num_iteraciones < 500:
		num_iteraciones += 1

		# Step 1
		new_vectores = find_near(vectores, clusters)

		# Step 2
		vectors_near_clusters = [[] for _ in range(num_clusters)]
		for vector in new_vectores:
			vectors_near_clusters[vector[1]].append(vector[0])
		new_clusters = [centroide(vs, dim_vectores) for vs in vectors_near_clusters]

		# print([distancia(c1, c2) for (c1, c2) in zip(clusters, new_clusters)], flush = True)

		diff = 0.0
		for (c1, c2) in zip(clusters, new_clusters):
			diff += math.sqrt(distancia(c1, c2))

		if diff < EPS:
			break

		clusters = new_clusters
		vectores = new_vectores

	print(num_iteraciones)

	# Plot the results
	for idx in range(num_clusters):
		plt.scatter(clusters[idx].get('0', 0), clusters[idx].get('1', 0), s = 300, c = COLORS[idx])

	for vector in vectores:
		plt.scatter(vector[0].get('0', 0), vector[0].get('1', 0), c = COLORS[vector[1]])

	plt.show()

	return clusters

# Conecta con los Workers y el Sink
context = zmq.Context()

# socket with workers
workers = context.socket(zmq.PUSH)
workers.bind("tcp://*:5557")

# socket with sink
sink_push = context.socket(zmq.PUSH)
sink_push.connect("tcp://localhost:5558")

sink_pull = context.socket(zmq.PULL)
sink_pull.bind("tcp://*:5556")


print("Presione Enter cuando los trabajadores esten listos...", flush = True)
_ = input()
print("Iniciando Clasificación", flush = True)


random.seed()
data = [generar_vector_aleatorio(2) for _ in range(1600)]

# Tiempo Inicial
time_start = time.time()

# Proceso
results = kmean(data, 2, 5)

# Tiempo Final
time_final = time.time()

print("Tiempo: ", time_final - time_start)