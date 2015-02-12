import csv, math, random
import heapq
import copy
def normalize_features(features):
	total = sum(features)
	return [float(x)/float(total) for x in features]

def euclidean_distance(a, b):
	assert len(a)==len(b), "lengths are not the same :("
	total = 0
	for i in range(0, len(a)):
		total += (a[i]-b[i])**2
	return math.sqrt(total)

def cos_distance(a, b):
	assert len(a)==len(b), "lengths are not the same :("
	dot_product = 0
	for i in range(0, len(a)):
		dot_product += a[i]*b[i]
	mag_a = 0
	mag_b = 0
	for i in range(0, len(a)):
		mag_a += a[i]**2
		mag_b += b[i]**2
	mag_a = math.sqrt(mag_a)
	mag_b = math.sqrt(mag_b)
	cos = (dot_product/(mag_a*mag_b))
	angle = math.acos(cos)*360/(2*3.14159)
	# print "the angle is "+str(angle)
	return angle

def generate_rankings(a, b):
	apeople = {}
	bpeople = {}
	for aperson in a:
		rankings = []
		for bperson in b:
			distance = cos_distance(aperson['features'], bperson['features'])
			heapq.heappush(rankings, (distance, bperson))
		apeople[aperson['name']] = [x[1]['name'] for x in rankings]
	for bperson in b:
		rankings = []	
		for aperson in a:
			distance = cos_distance(aperson['features'], bperson['features'])
			heapq.heappush(rankings, (distance, aperson))
		bpeople[bperson['name']] = [x[1]['name'] for x in rankings]
	return apeople, bpeople


def print_rankings(a, b):
	with open('preferences.txt', 'w') as outfile:
		for pref_list in (a, b):
			for person in pref_list.keys():
				outfile.write(person + ' rankings:\n')
				for r in pref_list[person]:
					outfile.write('\t'+r+'\n')

def read_csv(csv_file = 'match.csv'):
	a_people = []
	b_people = []
	c_people = []
	people = []
	#
	# read responses for csv file
	#
	with open(csv_file, 'rb') as match_form:
		reader = csv.reader(match_form)
		row_index = 0
		for row in reader:
			if row_index != 0:
				name = row[1]
				gender = row[2]
				preference = row[len(row)-1]
				features = []
				for i in range(3,len(row)-1):
					weight = row[i]
					if weight == "":
						weight = 0
					features.append(int(weight))
				features = normalize_features(features)
				#
				# add person to people list
				#
				person = {}
				person['name'] = name
				person['gender'] = gender
				person['preference'] = preference
				person['features'] = features
				people.append(person)
			row_index += 1

	#
	# split people into two classes
	# 
	for person in people:
		if person['preference'] != 'Male':
			if person['preference'] != 'Female':
				c_people.append(person)
			else:
				a_people.append(person)
		else:
			b_people.append(person)
	# randomize
	random.shuffle(a_people)
	random.shuffle(b_people)
	random.shuffle(c_people)
	with open('balance.txt', 'w') as outfile:
		#
		# do your best to balance with the no preference people
		#
		# outfile.write('these are the males and females'\n)
		# outfile.write([x['name'] for x in a_people])
		# outfile.write([x['name'] for x in b_people])
		# outfile.write([x['name'] for x in c_people])

		while len(c_people)>0:
			person = c_people.pop()
			outfile.write('using '+person['name']+' to balance\n')
			if len(a_people)<len(b_people):
				a_people.append(person)
				outfile.write("\tnow class A\n")
			else:
				b_people.append(person)
				outfile.write("\tnow class B\n")
		#
		# if balance not equal pick some from one class to move to the other
		#
		while(abs(len(a_people)-len(b_people))>1):
			if len(a_people)>len(b_people):
				person = a_people.pop()
				b_people.append(person)
				outfile.write('changing genders...'+person['name']+'to B\n')
			else:
				person = b_people.pop()
				a_people.append(person)
				outfile.write('changing genders...'+person['name']+'to A\n')

		outfile.write('these are the males and females after balancing\n')
		outfile.write(str([x['name'] for x in a_people])+'\n')
		outfile.write(str([x['name'] for x in b_people])+'\n')
		outfile.write(str([x['name'] for x in c_people])+'\n')

		lonely = None
		if abs(len(a_people)-len(b_people))==0:
			outfile.write('exactly balanced\n')
		else:
			if abs(len(a_people)-len(b_people))==1:
				outfile.write('somebody is going to be lonely\n')
				if len(a_people)>len(b_people):
					random.shuffle(a_people)
					lonely = a_people.pop()
				else:
					random.shuffle(b_people)
					lonely = b_people.pop()
			else:
				# move people around
				print 'moving peeps around'


		if lonely:
			outfile.write(lonely['name'] + ' will be lonely :( sad face\n')
	return a_people, b_people


def export_rankings(a, b):
	with open('men', 'w') as outfile:
		for m in a.keys():
			prefs = a[m]
			outfile.write(m+':\t')
			while len(prefs)>0:
				w = prefs[0]
				prefs = prefs[1:]
				outfile.write(w)
				if len(prefs)>0:
					outfile.write(',')
			outfile.write('\n')
	with open('women', 'w') as outfile:
		for m in b.keys():
			prefs = b[m]
			outfile.write(m+':\t')
			while len(prefs)>0:
				w = prefs[0]
				prefs = prefs[1:]
				outfile.write(w)
				if len(prefs)>0:
					outfile.write(',')
			outfile.write('\n')

a_people, b_people = read_csv('match.csv')
a_class, b_class = generate_rankings(a_people, b_people)
print_rankings(a_class, b_class)
export_rankings(a_class, b_class)

def stable_marriage(a, b):
	males_remaining = [x for x in a.keys()]
	assignments = {}
	while len(males_remaining)>0:
		a, b, assignments, males_remaining = do_round(a, b, assignments, males_remaining)
	return assignments
def do_round(a, b, assignments, males_remaining):
	kicked_out = []
	for male in males_remaining:
		pref_list = a[male]
		female = pref_list[0]
		a[male] = pref_list[1:]
		if female in assignments.keys():
			# check b for preference list
			preferences = b[female]
			old_male = assignments[female]
			# who is higher, male or old_name
			a_index = preferences.index(male)
			old_index = preferences.index(old_male)

			# print str(a_index) + ' and ' +str(old_index)
			if a_index>old_index:
				kicked_out.append(male)
			else:
				kicked_out.append(old_male)
				assignments[female] = male
		else:
			assignments[female] = male
	return a, b, assignments, kicked_out

# print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'




# with open('algorithm_results.txt', 'w') as outfile:
# 	print 'MALE OPTIMAL VERSION'
# 	print 'this version is optimal for '+str(a_class.keys())
# 	a_copy = copy.deepcopy(a_class)
# 	b_copy = copy.deepcopy(b_class)

# 	assignments = stable_marriage(a_class, b_class)
# 	for name in assignments.keys():
# 		print name + " + " + assignments[name]
# 		outfile.write(name + " + " + assignments[name] + "\n")

# 	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
# 	print 'FEMALE OPTIMAL VERSION'
# 	print 'this version is optimal for '+str(b_copy.keys())
# 	outfile.write('\n\n\n')
# 	assignments = stable_marriage(b_copy, a_copy)
# 	for name in assignments.keys():
# 		print name + " + " + assignments[name]
# 		outfile.write(name + " + " + assignments[name] + "\n")