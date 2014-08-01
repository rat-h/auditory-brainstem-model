#! /usr/bin/env python
import sys,os
try:
	import cPickle as pickle
except:
	import pickle

if len(sys.argv) < 2:
	sys.stderr.write("USAGE: check-pkl pklfile")
	sys.exit(1)
if not os.access(sys.argv[1],os.R_OK):
	sys.stderr.write("Couldn't read \'%s\' file"%sys.argv[1])
	sys.exit(1)
with open(sys.argv[1],"rb") as fd:
	while True:
		try: obj = pickle.load(fd)
		except: break
		sys.stdout.write(str(obj)+"\n")
