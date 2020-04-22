import zmq

context = zmq.Context()

fan = context.socket(zmq.PULL)
fan.bind("tcp://*:5558")

fan_push = context.socket(zmq.PUSH)
fan_push.connect("tcp://localhost:5556")

num_iteraciones = 0
while True:

	num_iteraciones += 1

	n_tasks = fan.recv_json()['n_tasks']
	# print(num_iteraciones, n_tasks, flush = True)

	vectores = []
	for task in range(n_tasks):
		response = fan.recv_json()['response']
		vectores = vectores + response

	fan_push.send_json({ 'response': vectores })