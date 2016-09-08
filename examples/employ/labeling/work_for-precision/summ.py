import csv

INPUT = "work_for_tagged.csv"
map = {}
map['t'] = [0,0,0]
map[''] = [0,0,0]
with open(INPUT, 'r') as file:
	next(file)
	reader = csv.reader(file)
	for row in reader:
		if row[-1]=='1':
			map[row[4]][0] += 1
		elif row[-1]=='UNKNOWN':
			map[row[4]][2] += 1
		else:
			map[row[4]][1] += 1
print(map)

'''
Result:
Labeled	correct	incorrect	unknown	Total
YES	8	7	1	16
NO	20	16	7	43
TOTAL	28	23	8	59
'''
