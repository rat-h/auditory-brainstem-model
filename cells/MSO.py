'''
This Cell Object defines the geometry and membrane properties of a 
bipolar Medial Superio Olive (MSO) of the mammalian brainstem.

Model configurations is described in 
	Zhou, Carney, and Colburn (2005) J. Neuroscience, 25(12):3046-3058

Ported	from: NEURON http://senselab.med.yale.edu/modeldb/ShowModel.asp?model=53869
		to NEURON+Python for auditory-brainstem model
		by Ruben Tikidji-Hamburyan
		2014/11/23
'''
try:
    import cPickle as pickle
except:
    import pickle
import logging
import numpy as np

from neuron import h

class MSOcell:
	def __init__(self, Param=None, NOISE = None, gid = None, pc=None):
		self.soma		= h.Section()
		self.soma.nseg	= 1
		self.soma.L		= 40	# um
		self.soma.diam	= 20	# um
		self.soma.Ra	= 200	#ohm.cm
		self.soma.cm	= 1.		# uF/cm2
		self.soma.insert('msona')
		self.soma(0.5).msona.gnabar	= 0.1
		self.soma(0.5).msona.gl		= 0.002
		
		self.soma.ena = 55
##		
#		self.soma.v_init = -62
##		
		#if NOISE != None:
			#self.innp = h.InNp(0.5, sec=self.soma)
			#self.rnd        = h.Random(np.random.randint(0,32562))
			#self.innp.noiseFromRandom(self.rnd)
			#self.innp.dur   = h.tstop
			#self.innp.delay = 0.9e9
			#self.innp.per   = 0.9e9
			#self.innp.mean  = 0.0
			#self.innp.stdev = 0.0

##
##
		self.axon		= h.Section()
		self.axon.nseg = 51
		self.axon.diam = 2 	#// um
		self.axon.L = 400 	#	// um
		self.axon.Ra=200 	#	// ohm.cm 
		self.axon.cm=1 		#// uF/cm2
		self.axon.insert('msokht')
		self.axon.insert('msoklt')
		self.axon.insert('msona')
		self.axon.insert('msoih')
		self.axon.ek, self.axon.ena, self.axon.eh=-70., 55., -43
		for seg in self.axon:
			seg.msokht.gkbar = 0.02   	#//S/cm2
			seg.msoklt.gkbar = 0.03 	
			seg.msona.gnabar = 0.3
			seg.msona.gl	 = 0.002	
			seg.msoih.ghbar	 = 0.0015   
		self.axon.ena = 55	#// mV
		self.axon.ek = -80	#// mV
##
##
		self.dends = [h.Section() for x in range(2)]
		self.ipsid = self.dends[1]
		self.contd = self.dends[0]
		for dend in self.dends:
			dend.nseg = 20
			dend.L = 200.0	#// um 
			dend.diam = 3	#// um
			dend.Ra = 200	#// ohm.cm 
			dend.cm = 1	#// uF/cm2
			dend.insert ('pas')
			for seg in dend:
				seg.pas.g = 0.002
				seg.pas.e = -65
##		
				#if NOISE != None:
					#self.innp = h.InNp(0.5,sec=seg) #????
##					self.innp = h.InNp(seg/nseg,sec=self.dend) #????
					#self.rnd        = h.Random(np.random.randint(0,32562))
					#self.innp.noiseFromRandom(self.rnd)
					#self.innp.dur   = h.tstop
					#self.innp.delay = 0.9e9
					#self.innp.per   = 0.9e9
					#self.innp.mean  = 0.0
					#self.innp.stdev = 0.0
##
##			
		self.axon.connect(self.dends[1],0.225,0)
		self.dends[0].connect(self.soma,0.0,0)
		self.dends[1].connect(self.soma,1.0,0)
##	
##
#RTH: Model self identifiers. ????
		self.model = 0
		self.modelname = None

		#############################################################################################
		#                                          RECORDERS                                        #
		#############################################################################################
		self.spks			= h.Vector()
		self.sptr			= h.APCount(0.95,sec=self.axon)
		self.sptr.thresh		= -10.
		self.sptr.record(self.spks)
		
		#############################################################################################
		#                                       PARAMETERS SETUP                                    #
		#############################################################################################
		if Param != None: self.setParams(Param)

		#############################################################################################
		#                                     Global identification                                 #
		#############################################################################################
		if gid != None:
			self.setgid(gid, pc)
		else:
			self.gid = None
	
	def setallgid(self, basegid, pc=None ):
		self.setgid(basegid, pc)
		return basegid + 1
		
	def setgid(self, gid, pc=None):
		self.gid = gid
		self.output = h.NetCon(self.axon(0.95)._ref_v,None,sec=self.axon)
		if not ( pc == None ):
			pc.set_gid2node(gid, pc.id())
			pc.cell(gid, self.output)
		return {'gid':gid, 'netcon':self.output, 'sec':self.axon}

	def setParams(self, Param=None):
		for param in Param:
			#TODO:because parameter maybe for dendrite or axon, we should
			#     make a loop for segments and set parameters not only in soma.
			try: exec "self.soma(0.5).{} = Param[\'{}\']".format(param,param)
			except BaseException as e:
				logging.error("Coudn't set up parameter %s: %s"%(param,e))
				raise ValueError("Wrong Parameter %s"%param) 

	def save(self, fd):
		pickle.dump(['spk',self.gid, np.array(self.spks)],fd)
##		
##		
		
#4testing
if __name__ == "__main__":
	MSO = MSOcell()

	h.celsius=22

	stim = h.IClamp(MSO.soma(0.5))
	stim.delay = 20.0
	stim.dur = 40
	stim.amp = 0.7

	print "stim.amp = ", stim.amp, "\nstim.dur = ", stim.dur, "\nstim.delay = ", stim.delay

	vs = h.Vector()
	vs.record(MSO.soma(0.5)._ref_v)
	va = h.Vector()
	va.record(MSO.axon(0.95)._ref_v)
	t = h.Vector()
	t.record(h._ref_t)

	h.tstop = 100.0

	h.run()

	##
	import matplotlib.pyplot as plt

	plt.plot(t,vs,"r-",t,va,"b-")
	spk =np.array(MSO.spks)
	plt.plot(spk, [0 for x in spk], "k|")
	plt.show()
