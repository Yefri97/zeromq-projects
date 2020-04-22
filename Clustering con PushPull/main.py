import time
import math
import random
from matplotlib import pyplot as plt

EPS = 0.000001
MAX_NUMBER = 10000
COLORS = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']

def generar_vector_aleatorio(dimension):
	return [random.randint(0, MAX_NUMBER) for _ in range(dimension)]


def generar_clusters_aleatorios(num_clusters, dim_vectores):
	return [generar_vector_aleatorio(dim_vectores) for _ in range(num_clusters)]


def distancia(vector1, vector2):
	dist = 0.0
	for (x1, x2) in zip(vector1, vector2):
		dist += (x1 - x2) * (x1 - x2)
	return math.sqrt(dist)


def centroide(vectores, dim):
	response = [0 for _ in range(dim)]
	for i in range(dim):
		for vector in vectores:
			response[i] += vector[i] * 1.0 / len(vectores)
	return response


def find_near(vectores, clusters):
	new_vectores = []
	for vector in vectores:
			cr_near = -1
			for idc in range(clusters.__len__()):
				if cr_near == -1 or distancia(vector[0], clusters[idc]) < distancia(vector[0], clusters[cr_near]):
					cr_near = idc
			new_vectores.append([vector[0], cr_near])
	return new_vectores


def kmean(vectores, dim_vectores, num_clusters):
	
	vectores = [[vector, -1] for vector in vectores]
	clusters = generar_clusters_aleatorios(num_clusters, dim_vectores)

	num_iteraciones = 0
	while True:
		num_iteraciones += 1

		# Step 1
		new_vectores = find_near(vectores, clusters)

		# Step 2
		vectors_near_clusters = [[] for _ in range(num_clusters)]
		for vector in new_vectores:
			vectors_near_clusters[vector[1]].append(vector[0])
		new_clusters = [centroide(vs, dim_vectores) for vs in vectors_near_clusters]

		are_similar = 1
		for (c1, c2) in zip(clusters, new_clusters):
			if math.fabs(distancia(c1, c2)) > EPS:
				are_similar = 0

		if are_similar:
			break

		clusters = new_clusters
		vectores = new_vectores

	print(num_iteraciones)

	# Plot the results
	"""for idx in range(num_clusters):
		plt.scatter(clusters[idx][0], clusters[idx][1], s = 300, c = COLORS[idx])

	for vector in vectores:
		plt.scatter(vector[0][0], vector[0][1], c = COLORS[vector[1]])

	plt.show()"""

	return clusters

random.seed()
data = [generar_vector_aleatorio(2) for _ in range(160000)]

# Tiempo Inicial
time_start = time.time()

# Proceso
results = kmean(data, 2, 5)

# Tiempo Final
time_final = time.time()

print("Tiempo: ", time_final - time_start)