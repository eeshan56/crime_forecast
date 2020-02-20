
import os

requirements = open('requirements.txt', 'r').read()
requirements = requirements.split("\n")

for i in range(len(requirements)):
	print("Package: {}".format(i))
	os.system('pip install ' + requirements[i])