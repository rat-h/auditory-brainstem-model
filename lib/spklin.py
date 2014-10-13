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
	def __init__(self, anconfig=None, isright = False, gid = None, pc=None):
		self.isright = bool(isright)
		self.anconfig = anconfig
		###### Make source sections ######	
		if anconfig == None:
			self.sections	= None
			self.ntotal		= None
		else:
			self.sections	= [ {'gid':None,'netcon':None,'sec':h.VecStim()} for x in anconfig for y in x[1:] ]
			self.ntotal		= len(self.sections)
			if gid != None:
				self.setallgid(gid, pc=pc)
	def readfile(self,filename):
		with open(filename,"rb") as fd:
			checksum	=  pickle.load(fd)
			self.params	=  pickle.load(fd)
			if self.isright:
				xxx			= pickle.load(fd)
				del xxx
				self.spk	= pickle.load(fd)
				self.params['auditory nerve configuration'] = self.params['auditory nerve configuration'][1]
			else:
				self.spk	= pickle.load(fd)
				self.params['auditory nerve configuration'] = self.params['auditory nerve configuration'][0]
				#xxx			= pickle.load(fd)
		if self.anconfig == None :
			self.anconfig = self.params[ 'auditory nerve configuration' ]
			self.sections	= [ {'gid':None,'netcon':None,'sec':h.VecStim()} for x in anconfig for y in x[1:] ]
			self.ntotal		= len(self.sections)
		elif self.anconfig != self.params[ 'auditory nerve configuration' ]:
			raise ValueError("Data file is damaged! Configuration of Auditory Nerve is wrong")
		elif self.sections == None:
			raise ValueError("Sections are destroyed")
				
		#### Check configuration and make vectors of spikes ####
		for an, spkset in zip( self.anconfig, self.spk):
			if an != spkset[0]:
				raise ValueError("Auditory Nerve at frequency {} chamle {} has different fiber types or size".format(an[0],"RIGHT" if self.isright else "LEFT") )
			for idx in xrange(len(spkset[1])):
				vector	= h.Vector(spkset[1][idx].shape[0])
				vector.from_python(spkset[1][idx])
				spkset[1][idx] = vector
		#### Setup Vectors ####
		for sec,vec in zip(self.sections, [ y  for x in self.spk for y in x[1] ] ):
			sec['sec'].play(vec)

	def setallgid(self, basegid, pc=None, syn=None):
		if self.anconfig == None : return None
		for idx,sec in enumerate(self.sections) :
			if sec['gid'] != None: continue
			if syn == None:
				sec['netcon']	= h.NetCon(sec['sec'],syn)
			else:
				sec['netcon']	= h.NetCon(sec['sec'],syn[idx])
			sec['gid']		= basegid+idx
			if not(pc == None):
				pc.set_gid2node(sec['gid'], pc.id())
				pc.cell(sec['gid'],sec['netcon'])
		return basegid + len(self.sections)

	def setParams(self, Param=None):
		pass

	#def get(self,freqid,fibid):
		#if freqid >= self.nhcell : return None
		#if fibid >= self.nfibpercell : return None
		#return self.sections[freqid][fibid]

	#def getid(self,freqid,fibid):
		#if freqid >= self.nhcell : return None
		#if fibid >= self.nfibpercell : return None
		#return self.sections[freqid][fibid]['gid']

	#def getfrtp(self,freqid=None,fibid=None):
		#def _rettypes(spkset,fibid=None):
			#if fibid == None: return spkset[1]
			#elif type(fibid) is list:
				#ret = []
				#for fib in fibid: ret+=[_rettypes(spkset,fibid=fib)]
				#return ret
			#elif fibid >= len(spkset[1]): return None
			#else : return spkset[1][fibid]
		#if freqid == None :
			#ret = []
			#for spk in xrange(self.nhcell):ret.append(self.getfrtp(freqid=spk,fibid=fibid))
			#return ret
		#elif type(freqid) is list :
			#ret = []
			#for freq in freqid:ret.append(self.getfrtp(freqid=freq,fibid=fibid))
			#return ret
		#elif freqid >= len(self.spk) : return None
		#else:
			#return (self.spk[freqid][0],_rettypes(self.spk[freqid],fibid=fibid))
	def save(self, fd):
		for sec,vec in zip(self.sections, [ y  for x in self.spk for y in x[1] ] ):
			pickle.dump(['spk',sec['gid'], np.array(vec)],fd)
		

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
