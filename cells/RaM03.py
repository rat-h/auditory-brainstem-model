'''
// Implementation of Rothman and Manis (2003a,b,c) VCN potassium channel
// models based on measured kinetics.
// This HOC file generates current clamp responses for 100 msec steps for each
// of the cell classes Type I-c (classic), Type I-t (transient), Type I-II, Type II-I
// and Type II, using the conductance levels listed in Table I of the third paper. 
// Requires individual mod files for ilt, ih, iht, ia, and ina, plus a leak channel.
// 
// 1 April 2004 for NEURON version 5.5
// Paul B. Manis
// pmanis@med.unc.edu
// 
// 2 April 2004.
// Added TypeII-o. This is an "octopus" cell model, assuming that the largest
// low-threshold conductance measurements in Figure 4 may have come from
// such cells, and based on data from Oertel's lab. The octopus cells are more
// than extreme bushy cells, but this is a starting point.
// Included Milgore's hcno octopus cell iH current model, just for the type II-o
// (octopus) cell model.

Ported to python Ruben Tikidji-Hamburyan
'''
try:
    import cPickle as pickle
except:
    import pickle
import logging
import numpy as np
from neuron import h


class vcnRaMbase:
	"""
	Python template for Rothman and Manis (2003a,b,c) VCN cells.
	Functions:
		Constructor(gid, Param=None, GUI=false, Nose=none) # sets up cell
			> gid		# global unique neuron ID for clustering and network
			> pc		# parallel context
			> Type:
				'Type I-c'	# classic (default)
				'Type I-t'	# transient 
				'Type I-II'
				'Type II-I'
				'Type II'	# Type II
				'Type IIo'	# Octopus cell
			> Param		# Dictionary of paramters
						# dict names should be the same as in mod file.
						# For example:
						# {vcnleak.erev:-65,vcnna.gnabar:1000}
			> Nose:
				None	# (default)

		setType(Type='Type I-c') # sets the parameters for different types
			> Type		# Same as above.
		
		setParams(Param=None) # sets parameters
			> Param		# Same as above.
				tuple	# (compartment name, location, parameter to record)
				list	# list of tuples like above.
			
		gettypespace()	# returns a list of embedded cell types.
		
		
		save(ffd)	# save spiketimes and extra recorded variables to file descriptor.
	"""
#		float		# stder of noise current in mA, mean=
#		{mean=float, std=float, delay=float, dur=float, per=float, n=int}
#	"""
	def __init__(self, Param=None, NOISE = None, Type=None, gid = None, pc=None):
		speccm = 0.9
		totcap =12						# total cap in pF for cell 
		self.somaarea = totcap *1E-6 / 1# pf -> uF,assumes 1 uF/cm2; result is in cm2 
		lstd = 1E4*h.sqrt(self.somaarea/h.PI)	# convert from cm to um 
		self.soma = h.Section(name='soma', cell=self)
		#self.soma.cm=1
		self.soma.cm = speccm			# change this here - minor difference.
		self.soma.nseg	= 1
		self.soma.diam	= lstd
		self.soma.L		= lstd
		self.soma.insert('vcnklt')
		self.soma.insert('vcnkht')	
		self.soma.insert('vcnna')
		self.soma.insert('vcnka')
		self.soma.insert('vcnih')
		self.soma.insert('vcnhcno')
		self.soma.insert('vcnleak')
		
		self.soma(0.5).vcnleak.g	= 1./10000.
		self.soma(0.5).vcnleak.erev = -65
		self.soma(0.5).vcnih.eh	= -43
		self.soma(0.5).vcnhcno.eh	= -43
		self.soma(0.5).vcnhcno.gbar = 0
		self.soma.Ra=150
		self.soma.ek = -70
		self.soma.ena	=  50
		#####
		## RTH: Not sure, this is a good idea!!!!
		#self.soma.usetable_vcnklt	= 0
		#self.soma(0.5).vcnna.usetable	= 0
		#self.soma(0.5).vcnkht.usetable	= 0
		#self.soma(0.5).vcnka.usetable	= 0
		#self.soma(0.5).vcnih.usetable	= 0
		#self.soma(0.5).vcnhcno.usetable	= 0
		
		#####
		#RTH: Model self identifiers.
		self.model					= 0
		self.modelname 				= None
				
		#############################################################################################
		#                                          RECORDERS                                        #
		#############################################################################################
		self.spks					= h.Vector()
		self.sptr					= h.APCount(.5,sec=self.soma)
		self.sptr.thresh			= -10.
		self.sptr.record(self.spks)
		

		#############################################################################################
		#                                     Global identification                                 #
		#############################################################################################
		if gid != None:
			self.setgid(gid, pc)
		else:
			self.gid = None

		#############################################################################################
		#                                       PARAMETERS SETUP                                    #
		#############################################################################################
		self.setType("Type I-c")
		if Type != None: self.setType(Type)
		self.setParams(Param)
	
	def setallgid(self, basegid, pc=None ):
		self.setgid(basegid, pc)
		return basegid + 1
		
	def setgid(self, gid, pc=None):
		self.gid = gid
		self.output = h.NetCon(self.soma(0.5)._ref_v,None,sec=self.soma)
		if pc != None:
			pc.set_gid2node(gid, pc.id())
			pc.cell(gid, self.output)
		return {'gid':gid, 'netcon':self.output, 'sec':self.soma}
	def setParams(self, Param=None):	
		if Param == None :
			return
		if not (type(Param) is dict) : 
			return
		for param in Param:
			try: exec "self.soma(0.5).%s = %g"%(param,Param[param])
			except BaseException as e:
				logging.error("Coudn't set up parameter %s: %s"%(param,e))
				raise ValueError("Wrong Parameter %s"%param) 
		
		
	def setType(self,Type):
		#############################################################################################
		#                                    Set up MODEL paramters                                 #
		#############################################################################################
		if Type == "Type I-c":
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(150)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(0)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(0)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(0.5)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(0)
			self.soma(0.5).vcnleak.g			= self.nstomho(2)
			self.vm						= -63.9
			self.model					= 1
			self.modelname 				= "Type I-c"
			#DB>>
			#print "Type I-c",self.gid
			#<<DB
		elif Type == "Type I-t":
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(80)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(0)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(65)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(0.5)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(0)
			self.soma(0.5).vcnleak.g			= self.nstomho(2)
			self.vm						= -64.2
			self.model					= 2
			self.modelname 				= "Type I-t"
		elif Type == "Type I-II":
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(150)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(20)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(0)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(2)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(0)
			self.soma(0.5).vcnleak.g			= self.nstomho(2)
			self.vm						= -64.1
			self.model					= 3
			self.modelname 				= "Type I-II"
		elif Type == 'Type II-I':
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(150)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(35)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(0)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(3.5)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(0)
			self.soma(0.5).vcnleak.g			= self.nstomho(2)
			self.vm						= -63.8
			self.model					= 4
			self.modelname 				= "Type II-I"
		elif Type == 'Type II':
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(150)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(200)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(0)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(20)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(0)
			self.soma(0.5).vcnleak.g			= self.nstomho(2)
			self.vm						= -63.6
			self.model					= 5
			self.modelname 				= "Type II"
			#DB>>
			#print "Type II",self.gid
			#<<DB
		elif Type == 'Type II-o':
			self.soma(0.5).vcnna.gnabar		= self.nstomho(1000)
			self.soma(0.5).vcnkht.gkhtbar	= self.nstomho(150)
			self.soma(0.5).vcnklt.gkltbar	= self.nstomho(600)
			self.soma(0.5).vcnka.gkabar		= self.nstomho(0)
			self.soma(0.5).vcnih.ghbar		= self.nstomho(0)
			self.soma(0.5).vcnhcno.gbar		= self.nstomho(40)
			self.soma(0.5).vcnleak.g		= self.nstomho(2)
			self.vm						= -66.67
			self.model					=  6
			self.modelname 				= "Type II-o (Octopus)"
	def nstomho(self,nanosiemens):
		"""
		convert from nanosiemens to mho/cm2.
		"""
		#self.somaarea = h.PI*self.soma.diam*self.soma.L*1e-6 #????
		return (1E-9*nanosiemens/self.somaarea)
	def gettypespace(self):
		return ('Type I-c', 'Type I-t', 'Type I-II', 'Type II-I', 'Type II', 'Type II-o')
	def save(self, fd):
		pickle.dump(['spk',self.gid, np.array(self.spks)],fd)


if __name__ == "__main__":
#	import numpy as np
	import matplotlib.pyplot as plt
	import sys,os
	h.celsius=22         					# base model temperature - temp at which measurements were made

	#########################
	#    Get param table    #
	cell = vcnRaMbase(0)
	params = []
	for T in cell.gettypespace():
		cell.setType(T)
		params.append( (
			T, 
			cell.soma(0.5).vcnna.gnabar,
			cell.soma(0.5).vcnkht.gkhtbar,
			cell.soma(0.5).vcnklt.gkltbar,
			cell.soma(0.5).vcnka.gkabar,
			cell.soma(0.5).vcnih.ghbar,
			cell.soma(0.5).vcnhcno.gbar,
			cell.soma(0.5).vcnleak.g
		) )
	for column in map(None, ("Type","GNa","GKht","GKlt","GKa","GH","GHo","Gl"), xrange(len(params[0]))):
		sys.stdout.write(column[0])
		for p in params:
			if column[1] == 0:
				sys.stdout.write("\t%s"%p[column[1]])
			else:
				sys.stdout.write("\t%g"%p[column[1]])
		sys.stdout.write("\n")
	#########################

	#### Extra functions ####
	def run(cell,icur):
		"""
		if icur is equal to None, then we need to set the currents for an IV
		if icur is int, then we need to set currents with particular steps
		"""
		h.tstop = 100
		t = h.Vector()
		t.record(h._ref_t)
		for i in icur:
			ic.delay=5
			ic.dur=100
			ic.amp=i/1000
			#DB>
			#print ic.amp
			#<DB
			cell.soma(0.5).vcnleak.erev = -65
			cell.soma(0.5).v=cell.vm
			h.finitialize(cell.vm)
			h.fcurrent()
			h.t=0
			while h.t < h.tstop*1.5: # go past end of pulses
				h.fadvance()
			plt.plot(t,cell.volt,label="%g"%i)

	def createcell(cell,Fig):
		if Fig == 'Fig2A':
			cell.setType("Type I-c")
			icur = [50., -50.]
			modelname = "Fig.2A: Type I-c +/- 50 pA"
		elif Fig == 'Fig2B':
			cell.setType("Type I-t")
			icur = [50., -50.]
			modelname = "Fig.2B: Type I-c +/- 50 pA"
		elif Fig == 'Fig2C':
			cell.setType("Type II")
			icur = [300., -300.]
			modelname = "Fig.2C: Type II  +/- 300 pA"
		elif Fig == 'Fig2D':
			cell.setType("Type I-II")
			icur = [100., -100.]
			modelname = "Fig.2D: Type I-II +/- 100 pA"

		elif Fig == 'Fig3A':
			cell.setType("Type II")
			icur = [300., -300.]
			modelname = "Fig3A: Type II, standard"
		elif Fig == 'Fig3B':
			cell.setType("Type II")
			cell.soma(0.5).vcnih.ghbar = cell.nstomho(0)
			icur = [300., -300.]
			modelname = "Fig3B. Type II, Ih = 0"
		elif Fig == 'Fig3C':
			cell.setType("Type II")
			cell.soma(0.5).vcnkht.gkhtbar = cell.nstomho(0)
			icur = [300., -300.]
			modelname = "Fig3C. Type II, IHT=0 (no high threshold)"
		elif Fig == 'Fig3D':
			cell.setType("Type II")
			cell.soma(0.5).vcnklt.gkltbar = cell.nstomho(0)
			icur = [150., -300.]
			modelname = "Fig3D. Type II, ILT=0 (no low threshold)"
		elif Fig == 'Fig4A':
			cell.setType("Type II")
			icur = [300., 500., 700.]
			modelname = "Fig4. Inset, Type II"
		elif Fig == 'Fig4B':
			cell.setType("Type I-II")
			icur = [90., 120., 550.]
			modelname = "Fig4. Inset, Type I-II"
		elif Fig == 'Fig4C':
			cell.setType("Type II-I")
			icur = [100., 300., 550.]
			modelname = "Fig4. Inset, Type II-I"
		elif Fig == 'Fig4D':
			cell.setType("Type I-c")
			icur = [50., 100., 150.]
			modelname = "Fig4. Inset, Type I-c"


		#//------------------------------------
		#// General Model Selection
		#// --- access to full IVs
		#//------------------------------------

		elif Fig == 'Type I-c':
			cell.setType("Type I-c")
			ncur,imax = 11,150.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type I-c"
		elif Fig == 'Type I-t':
			cell.setType("Type I-t")
			ncur,imax = 11,150.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type I-t"
		elif Fig == 'Type I-II':
			cell.setType("Type I-II")
			ncur,imax = 11,250.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type I-II"
		elif Fig == 'Type II-I':
			cell.setType("Type II-I")
			ncur,imax = 11,350.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type II-I"
		elif Fig == 'Type II':
			cell.setType("Type II")
			ncur,imax = 11,1000.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type II"
		elif Fig == 'Type II-o':
			cell.setType("Type II-o")
			ncur,imax = 11,2000.
			icur = [-imax+(i*(2*imax)/(ncur-1)) for i in xrange(ncur)]
			modelname = "Current Clamp IV, Type II-o (Octopus)"

		else:
			sys.stderr.write("Unknown Figure request: %s\nRequest should be on from follows:\n Fig2A Fig2B Fig2C Fig2D\n\n"%Fig)
			return (None,None,None)
		return (cell,icur,modelname)


	####    Main test    ####
	
	del cell
	cell = vcnRaMbase(0, GUI=True)
	plt.figure(1)
	for mn, mi in map(None,('Fig2A','Fig2B','Fig2C','Fig2D'),xrange(4)):
		plt.subplot(4,3,mi*3+1)
		c,icur,modename = createcell(cell,mn)
		if cell == None: sys.exit(1)
		ic = h.IClamp(0.5, sec=cell.soma)
		run(cell,icur)
		plt.title(modename)
		print modename,"is done"
		del icur,modename,ic
	for mn, mi in map(None,('Fig3A','Fig3B','Fig3C','Fig3D'),xrange(4)):
		plt.subplot(4,3,mi*3+2)
		c,icur,modename = createcell(cell,mn)
		if cell == None: sys.exit(1)
		ic = h.IClamp(0.5, sec=cell.soma)
		run(cell,icur)
		plt.title(modename)
		print modename,"is done"
		del icur,modename,ic
	for mn, mi in map(None,('Fig4A','Fig4B','Fig4C','Fig4D'),xrange(4)):
		plt.subplot(4,3,mi*3+3)
		c,icur,modename = createcell(cell,mn)
		if cell == None: sys.exit(1)
		ic = h.IClamp(0.5, sec=cell.soma)
		run(cell,icur)
		plt.title(modename)
		print modename,"is done"
		del icur,modename,ic
	
	plt.figure(2)
	for mn, mi in map(None,('Type I-c','Type I-t','Type I-II','Type II-I','Type II','Type II-o'),xrange(6)):
		plt.subplot(2,3,mi+1)
		c,icur,modename = createcell(cell,mn)
		if cell == None: sys.exit(1)
		ic = h.IClamp(0.5, sec=cell.soma)
		#DB>>
		#print icur
		#<<DB
		run(cell,icur)
		plt.title(modename)
		#plt.legend(loc=3)
		print modename,"is done"
		del icur,modename,ic

	plt.show()
	sys.exit(0)
