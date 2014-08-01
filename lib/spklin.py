import sys, os, csv, glob, logging
try:
    import cPickle as pickle
except:
    import pickle

import numpy as np
import numpy.random as rnd
from neuron import h

class spklin():
	"""
	Class spklin reads files with output auditory model and provides
	NetCons as a spike sources to netcons
	"""
	def __init__(self,nhcell=None, nfibpercell = None,isright = False, gid = None, pc=None):
		self.isright = bool(isright)
		self.nhcell, self.nfibpercell = nhcell, nfibpercell
		###### Make source sections ######	
		if nhcell == None or nfibpercell == None:
			self.sections	= None
			self.ntotal		= None
		else:
			self.ntotal		= self.nhcell * self.nfibpercell
			self.sections	= [ [ {'gid':None,'netcon':None, 'sec':h.VecStim()} for y in xrange(self.nfibpercell) ] for i in xrange(self.nhcell) ]
			if gid != None:
				self.setallgid(gid, pc=pc)
	def readfile(self,filename):
		with open(filename,"rb") as fd:
			self.params	=  pickle.load(fd)
			if self.isright:
				xxx			= pickle.load(fd)
				del xxx
				self.spk	= pickle.load(fd)
			else:
				self.spk	= pickle.load(fd)
				#xxx			= pickle.load(fd)
		if self.nhcell == None :
			self.nhcell = self.params[ 'number-hair-cells' ]
		if self.nfibpercell == None:
			self.nfibpercell = self.params[ 'fiber-per-hcell' ]
		if self.ntotal == None:
			self.ntotal		= self.nhcell * self.nfibpercell
		if self.nhcell != self.params[ 'number-hair-cells' ] \
			or self.nfibpercell != self.params[ 'fiber-per-hcell' ] \
			or self.ntotal	!= (self.params[ 'number-hair-cells' ] * self.params[ 'fiber-per-hcell' ]):
			logging.error("Data file is damaged! Parameters in file are wrong")
			raise ValueError("Data file is damaged! Parameters in file are wrong")
		if self.sections == None:
			self.sections	= [ [ {'gid':None,'netcon':None, 'sec':h.VecStim()} for y in xrange(self.nfibpercell) ] for i in xrange(self.nhcell) ]
				
		###### Checking parameters for maping ######
		if self.nhcell != len(self.spk):
			logging.error("Data file is damaged! Parameters in file are wrong")
			raise ValueError("Data file is damaged! Parameters in file are wrong")
		for fr,tp,spkset in self.spk:
			if len(tp) != self.nfibpercell or len(spkset) != self.nfibpercell:
				logging.error("Data file is damaged! Parameters in file are wrong")
				raise ValueError("Data file is damaged! Parameters in file are wrong")
		for freqid in xrange(self.nhcell):
			for fibid in xrange(self.nfibpercell):
				vector	= h.Vector(self.spk[freqid][2][fibid].size)
				vector.from_python(self.spk[freqid][2][fibid])
				self.spk[freqid][2][fibid] = vector
				self.sections[freqid][fibid]['sec'].play(vector)

	def setallgid(self, basegid, pc=None):
		if self.nhcell == None or self.nfibpercell == None \
			or self.sections == None or self.ntotal == None : return None
		gid = basegid
		for freqid in xrange(self.nhcell):
			for fibid in xrange(self.nfibpercell):
				self.setgid(freqid, fibid, gid, pc)
				gid += 1
		return gid

	def setgid(self,freqid,fibid,gid,pc=None,syn=None):
		if freqid >= self.nhcell : return None
		if fibid >= self.nfibpercell : return None
		if self.sections[freqid][fibid]['gid'] != None:
			return self.sections[freqid][fibid]
		netcon = h.NetCon(self.sections[freqid][fibid]['sec'],syn)
		self.sections[freqid][fibid]['gid']		= gid
		self.sections[freqid][fibid]['netcon']	= netcon
		if not(pc == None):
			pc.set_gid2node(gid, pc.id())
			pc.cell(gid,netcon)
		return self.sections[freqid][fibid]

	def setParams(self, Param=None):
		pass

	def get(self,freqid,fibid):
		if freqid >= self.nhcell : return None
		if fibid >= self.nfibpercell : return None
		return self.sections[freqid][fibid]

	def getid(self,freqid,fibid):
		if freqid >= self.nhcell : return None
		if fibid >= self.nfibpercell : return None
		return self.sections[freqid][fibid]['gid']

	def getfrtp(self,freqid=None,fibid=None):
		def _rettypes(spkset,fibid=None):
			if fibid == None: return spkset[1]
			elif type(fibid) is list:
				ret = []
				for fib in fibid: ret+=[_rettypes(spkset,fibid=fib)]
				return ret
			elif fibid >= len(spkset[1]): return None
			else : return spkset[1][fibid]
		if freqid == None :
			ret = []
			for spk in xrange(self.nhcell):ret.append(self.getfrtp(freqid=spk,fibid=fibid))
			return ret
		elif type(freqid) is list :
			ret = []
			for freq in freqid:ret.append(self.getfrtp(freqid=freq,fibid=fibid))
			return ret
		elif freqid >= len(self.spk) : return None
		else:
			return (self.spk[freqid][0],_rettypes(self.spk[freqid],fibid=fibid))
	def save(self, fd):
		for freqid in xrange(self.nhcell):
			for fibid in xrange(self.nfibpercell):
				pickle.dump(['spk',self.sections[freqid][fibid]['gid'], np.array(self.spk[freqid][2][fibid])],fd)
		

if __name__ == "__main__":
	from pprint import pprint
	print sys.argv	
	test = spklin()
	test.readfile(sys.argv[-2])
	pprint( test.getfrtp() )
	cell = h.Section()
	cell.L = 40.
	cell.diam = 20.
	cell.nseg = 1
	cell.insert("pas")
	cell.g_pas = 0.000001
	cell.e_pas = -65
	vrec = h.Vector()
	vrec.record(cell(0.5)._ref_v)
	trec = h.Vector()
	trec.record(h._ref_t)
	h.tstop=1000
	syn = h.Exp2Syn(0.5,sec=cell)
	syn.e=0
	syn.tau1=0.1
	syn.tau2=2
	###OLD fashioned straightforward way.
	#nc = test.setgid(6,1,1,syn=syn)['netcon']
	#>it works
	
	###Enpty syn variable should get target None
	#nc = test.setgid(6,1,1) ['netcon']#get netcon with None(nil) traget
	#nc.setpost(syn) #set target to syn
	#nc.active(True)
	#>it works
	
	###Connection trough pc
	pc = h.ParallelContext()
	test.setgid(1,1,1,pc=pc)
	#test.setallgid(0,pc=pc)
	for f in test.sections: 
		print ">>"
		for t in f: print "    ",t
	nc = pc.gid_connect(1.,syn)
	print "nc.srcgid(): ",nc.srcgid()
	#it works....
	
	nc.delay = 1
	nc.weight[0] = 0.001
	h.run()
	import matplotlib.pyplot as plt
	plt.plot(trec,vrec)
	plt.show()
