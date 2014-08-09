try:
    import cPickle as pickle
except:
    import pickle
import logging
import numpy as np

from neuron import h

class LSOcell:
	def __init__(self, Param=None, NOISE = None, gid = None, pc=None):
		self.soma		= h.Section()
		self.soma.nseg	= 1
		self.soma.L		= 23	# um
		self.soma.diam	= 11	# um
		self.soma.Ra	= 150	#ohm.cm
		self.soma.cm	= 1.		# uF/cm2
##		
		self.soma.insert('lsosoma')
		self.soma(0.5).lsosoma.gkbar		= 0.055
		self.soma(0.5).lsosoma.delta0		= 0.18 #// 0.9 // 0.8
		self.soma.insert('lsocaconc')
		self.soma(0.5).lsocaconc.depth		= 1.2e-06 	#// cm
		self.soma(0.5).lsocaconc.Pumptau	= 20.0 		#// ms
		self.soma.insert('lsotca')
		self.soma(0.5).lsotca.gcabar		= 0.015 	#// mho/cm2 !!!It seems, this is a wrong units. should be mS/cm2 :(
		self.soma(0.5).lsotca.gahpbar		= 0.021		#// mho/cm2
		self.soma.insert('lsoKv11')
		self.soma(0.5).lsoKv11.gKv1_1bar	= 0.0052	#// mS/cm2
		self.soma.insert('lsoh')
		self.soma(0.5).lsoh.eh = -38
##		
		self.soma.ena = 55	#// mV
		self.soma.ek = -80	#// mV
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
		self.axon.nseg = 1
		self.axon.diam = 3 	#// um
		self.axon.L = 70 	#	// um
		self.axon.Ra=150 	#	// ohm.cm 
		self.axon.cm=1 		#// uF/cm2
#
		self.axon.insert('lsoaxon')
#
		self.axon.ena = 55	#// mV
		self.axon.ek = -80	#// mV
#		self.axon.v_init = -62
##
##
		self.dends = [h.Section() for x in range(2)]
		for dend in self.dends:
			dend.nseg = 10
			dend.L = 282.0	#// um 
			dend.diam = 3.4	#// um
			dend.Ra = 150	#// ohm.cm 
			dend.cm = 1	#// uF/cm2
			Rm = 3000	#// ohm.cm2
			dend.insert ('pas')
			for seg in dend:
				seg.pas.g = 1/Rm
				seg.pas.e = -66
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
		self.axon.connect(self.soma,0.5,0)
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
		self.sptr			= h.APCount(0.5,sec=self.axon)
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
		self.output = h.NetCon(self.axon(0.5)._ref_v,None,sec=self.axon)
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
if __name__ is "__main__":
	LSO = LSOcell()

	h.celsius=22

	stim = h.IClamp(LSO.soma(0.5))
	stim.delay = 20.0
	stim.dur = 40
	stim.amp = 1.7

	print "stim.amp = ", stim.amp, "\nstim.dur = ", stim.dur, "\nstim.delay = ", stim.delay

	v = h.Vector()
	v.record(LSO.soma(0.5)._ref_v)
	t = h.Vector()
	t.record(h._ref_t)

	h.tstop = 100.0

	h.run()

	##
	import matplotlib.pyplot as plt

	plt.plot(t,v)
	plt.show()
