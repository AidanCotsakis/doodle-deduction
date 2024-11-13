
data = []

for i in range(38,62):
	with open(f"queue[{i}].txt", 'r') as f:
		data.append(f.read())

left = []
right = []
for i in data:
	left.append(int(i.split(",")[0]))
	right.append(int(i.split(",")[1]))

def average(arr):
	total = 0

	for i in arr:
		total += i

	return 	total/len(arr)

print(average(left), average(right))

