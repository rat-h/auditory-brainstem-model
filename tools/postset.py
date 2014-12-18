"""
Postset procedure post simulation analyses
"""
import sys,os, hashlib, types, glob
try:
	import cPickle as pickle
except:
	import pickle
import logging,time
import numpy as np

from tools.commonvariables import stimlist,stimnames

def collector(stimname,stimobj,config):
	logging.debug(" > heck hash and number of hosts")
	if not os.access(stimobj[3]+"%03d"%config["GENERAL"]["NODEID"],os.R_OK):
		logging.error("Couldn't access to root file %s"%stimobj[3])
		return None
	nodes = None
	with open(stimobj[3]+"%03d"%config["GENERAL"]["NODEID"],'rb') as fd:
		while True:
			try: obj=pickle.load(fd)
			except: break
			if obj[0] == "h":
				if obj[1] != config["GENERAL"]["NETWORKHASH"]:
					logging.error("Hash sums don't match config:%s, %s:%s "%(config["GENERAL"]["NETWORKHASH"],stimobj[3]+"%03d"%config["GENERAL"]["NODEID"],obj[1] ) )
					return None
				else:
					nodes = obj[-1]
					break
	if nodes == None:
		logging.error("Couldn't header record in root file %s"%stimobj[3])
		return None
	logging.debug(" > number of hosts was {}".format(nodes))
	logging.debug(" > read networkfile '%s' for population index"%config["GENERAL"]['networkfilename'])
	poplist = {}
	reclist = {}
	gidlist = []
	timeoffset = 0
	if not os.access(config["GENERAL"]['networkfilename'],os.R_OK):
		logging.error("Couldn't access to network file %s"%config["GENERAL"]['networkfilename'])
		return None
	with open(config["GENERAL"]['networkfilename'],'rb') as fd:
		try:
			hsum = pickle.load(fd)
		except:
			logging.error("Network file %s is empty!"%config["GENERAL"]['networkfilename'])
			return None
		if  hsum != config["GENERAL"]["NETWORKHASH"]:
			logging.error("Hash sums don't match config:%s, %s:%s "%(config["GENERAL"]["NETWORKHASH"],config["GENERAL"]['networkfilename'],hsum ) )
			return None
		while True:
			try: obj=pickle.load(fd)
			except: break
			if obj[0] == 'p':
				for x in obj[2]:
					if type(x) is tuple:
						gidlist += [ [a,obj[1]] for a in range(x[0],x[1]+1) ]
					else:
						gidlist += [ [x,obj[1]] ]
				poplist[ obj[1] ] = []
			if obj[0] == 'rc':
				reclist[ obj[3] ] = []
	gidlist.sort()

	
	for hid in xrange(nodes):
		if not os.access(stimobj[3]+"%03d"%hid,os.R_OK):
			logging.error("Couldn't access to record file %s"%stimobj[3]+"%03d"%hid)
			return None
		with open(stimobj[3]+"%03d"%hid,"rb") as fd:
			while True:
				offset = fd.tell()
				try: obj=pickle.load(fd)
				except: break
				if obj[0] == "h":
					if  obj[1] != config["GENERAL"]["NETWORKHASH"]:
						logging.error("Hash sums don't match config:%s, %s:%s "%(config["GENERAL"]["NETWORKHASH"],stimobj[3]+"%03d"%hid,obj[1] ) )
						return None
					if obj[3] != nodes:
						logging.error(" Wrong number of nodes(%d) in file %s "%(obj[3],stimobj[3]+"%03d"%hid) )
						return None
					continue
				if obj[0] == "spk":
					gidlist[obj[1]].append( [hid,offset] )
				if obj[0] == 'rec':
					reclist[ obj[1] ] += [ [ obj[2], (hid,offset) ] ]
				if obj[0] == 'time':
					timeoffset = (hid,offset)

	for g in gidlist:
		poplist[g[1]].append( (g[0],g[2]) )
	del gidlist

	with open(stimobj[3],'wb') as fd:
		pickle.dump(config["GENERAL"]["NETWORKHASH"],fd)
		pickle.dump(nodes,fd)
		pickle.dump(poplist,fd)
		pickle.dump(reclist,fd)
		pickle.dump(timeoffset,fd)
	stimlist[stimname] = (poplist,reclist,timeoffset,None,[ open(stimobj[3]+"%03d"%hid,'rb') for hid in xrange(nodes)] )
	return config
	
def collect(config):
	global stimnames
	logging.info("COLLECT SIMULATION RESULTS:")
	for stim in config["STIMULI"]['stimuli']:
		if type(stim) is str:
			if not stim in config["STIMULI"]:
				logging.error("couldn't find '%s' in STIMULI section"%stim)
				return None
			stimname = stim
			stimobj = config["STIMULI"][stim]
		else:
			stimobj = stim
			for names in config["STIMULI"]:
				if config["STIMULI"][names] == stim:
					stimname = names
					break
		stimnames.append(stimname)
		if not os.access(stimobj[3],os.R_OK):
			logging.debug(" > %s file do not exists, try to collect"%stimobj[3])
			config = collector(stimname,stimobj,config)
			if config =={} or config == None: return None
		else:
			with open(stimobj[3],'rb') as fd:
				try:
					hsum = pickle.load(fd)
				except:
					logging.debug(" > File {} is empty, try to recollect".format(stimobj[3]))
					config = collector(stimname,stimobj,config)
					if config =={} or config == None: return None
					else: break
				if hsum != config["GENERAL"]["NETWORKHASH"]:
					logging.debug(" > Hash sum of %s doesn't match to config file, try to recollect"%stimobj[3])
					config = collector(stimname,stimobj,config)
					if config =={} or config == None: return None
					else: continue
				nodes = pickle.load(fd)
				poplist = pickle.load(fd)
				reclist = pickle.load(fd)
				timeoffset = pickle.load(fd)
			stimlist[stimname] = (poplist,reclist,timeoffset,None,[ open(stimobj[3]+"%03d"%hid,'rb') for hid in xrange(nodes)])
		logging.info(" > %s is done"%stimname)
	#DB>
	#print stimnames
	#<DB
	return config
