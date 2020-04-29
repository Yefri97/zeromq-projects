import zmq

class SinkKMean:

	def __init__(self):

		context = zmq.Context()

		self.fan = context.socket(zmq.PULL)
		self.fan.bind("tcp://*:5558")

		self.fan_push = context.socket(zmq.PUSH)
		self.fan_push.connect("tcp://localhost:5556")


	def do(self):
		# Process tasks forever
		while True:

			s = self.fan.recv_json()
			n_tasks = s['n_tasks']
			n_clusters = s['n_clusters']

			counter = [0 for _ in range(n_clusters)]
			centroids = [{} for _ in range(n_clusters)]
			for task in range(n_tasks):
				response = self.fan.recv_json()['response']
				for i, cluster in enumerate(response):
					for dim in cluster:
						if dim == 'counter':
							counter[i] += cluster[dim]
							continue
						if dim not in centroids[i]:
							centroids[i][dim] = 0.0
						centroids[i][dim] += cluster[dim]

			for i, centroid in enumerate(centroids):
				for dim in centroid:
					centroid[dim] /= counter[i]

			self.fan_push.send_json({ 'response': centroids })


def main():
	sink = SinkKMean()
	print("Sink Listo...", flush = True)
	sink.do()

if __name__ == '__main__':
	main()