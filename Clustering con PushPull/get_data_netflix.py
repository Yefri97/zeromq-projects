import time
import json

def read_netflix_data(limit):
	
	folder = 'netflix-prize-data/'
	files = ['combined_data_' + str(i+1) + '.txt' for i in range(4)]

	movie = 0
	data = {}
	for file in files:
		cnt = 0
		with open(folder + file, 'r') as f:
			for line in f.readlines():
				if line[-2] == ':':
					movie += 1
					if movie > limit:
						return data
				else:
					(user, rank, date) = line.split(',')
					if user not in data:
						data[user] = {}
					data[user][str(movie - 1)] = int(rank)
				cnt += 1
		print(file + ": Se procesaron " + str(cnt) + " lineas.", flush = True)
	return data
	
def save_netflix_data(data):
	ranks = []
	users = []

	for key, value in data.items():
		users.append(int(key))
		ranks.append(value)

	with open('data/ranks.txt', 'w') as f:
		f.write(json.dumps(ranks))

	with open('data/users.txt', 'w') as f:
		f.write(json.dumps(users))

time_start = time.time()
save_netflix_data(read_netflix_data(100))
time_final = time.time()
print("Tiempo: ", time_final - time_start)