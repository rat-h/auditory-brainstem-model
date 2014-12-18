import os,sys,csv,time
import numpy as np
try:
    import cPickle as pickle
except:
    import pickle
import logging,time

#### Import HOME directory with 'tools' ####
if os.path.basename(sys.argv[0]) == "nrniv" :
	for arg in sys.argv:
		if len(arg) < len("mainmodel.py"): continue
		if arg[-len("mainmodel.py"):] == "mainmodel.py":
			homedir = os.path.dirname(arg)
			break
else:
	homedir = os.path.dirname(sys.argv[0])
if homedir == "" : homedir = "./"
sys.path.insert(0,homedir)
sys.path.insert(0,homedir+"/tools")

from tools.confreader import confreader as confreader
from tools.preset import checkgeneralsettings, presetstimuli, presetnetwork, hashsum, presetmodules
from tools.postset import collect
from tools.commonvariables import *

def pcexit(status):
	if pycore == 'nrniv':
		pc.runworker()
		time.sleep(3)
		pc.done()
	logging.info("TERMINATED WITH STATUS %d"%status)
	logging.info("#############################\n\n")
	exit(status)


config["CONF"] = {}
config["CONF"]["file"] 		= "mainmodel.cfg"
config["CONF"]["log"]		= None
config["CONF"]["log-level"]	= 'DEBUG' #'INFO'
config["CONF"]["run"]		= True
config["CONF"]["compiler"]	= "nrnivmodl"
config["CONF"]["preset"]	= False
config["CONF"]["parallel"]	= True
config["CONF"]["threads"]	= 4
config["CONF"]["collect"]	= False
config["CONF"]["graphs"]	= False
config["CONF"]["view"]		= False
config["CONF"]["stat"]		= False
config["CONF"]["conf-exp"]	= None


config["CONF"]["mpi"]		= False


for arg in sys.argv:
	if arg[:len("--config=")] == "--config=":
		config["CONF"]["file"] 	= arg[len("--config="):]
	if arg[:len("--log=")] == "--log=":
		config["CONF"]["log"] 	= arg[len("--log="):]
	if arg[:len("--log-level=")] == "--log-level=":
		config["CONF"]["log-level"] 	= arg[len("--log-level="):]
	if arg == "--no-run":
		config["CONF"]["run"]		= False
	if arg[:len("--mod-compiler=")] == "--mod-compiler=":
		config["CONF"]["compiler"] 	= arg[len("--mod-compiler="):]
	if arg == "--preset-only":
		config["CONF"]["preset"]	= True
	if arg == "--non-parallel":
		config["CONF"]["parallel"]	= False
	if arg == "--non-threads":
		config["CONF"]["threads"]	= -1
	if arg == "--collect":
		config["CONF"]["collect"]	= True
	if arg == "--graphs":
		config["CONF"]["graphs"]	= True
	#if arg == "--view":
		#config["CONF"]["view"]		= True
	if arg == "--stat":
		config["CONF"]["stat"]		= True
	if arg[:len("--config-exp=")] == "--config-exp=":
		config["CONF"]["conf-exp"]	= arg[len("--config-exp="):]
	if arg == "-mpi":
		config["CONF"]["mpi"]		= True

	if arg[:len("-h")] == "-h" or arg[:len("-help")] == "-help" or\
	   arg[:len('--h')] == '--h' or arg[:len("--help")] == "--help" or\
	   arg[:len('/?')] == '/?':
		sys.stdout.write("\nUSAGE: python|nrngui -nogui -python|mpirun -hosts... -h nrngui -nogui -python -mpi|something_else mainmodel.py [OPTIONS]\n")
		sys.stdout.write("OPTIONS:\n")
		sys.stdout.write("   -h|-help|--h|--help            : prints this help and exit\n")
		sys.stdout.write("   --config=configuration_file    : sets configuration file [default: mainmodel.cfg]\n")
		sys.stdout.write("   --log=log_file                 : sets log file [default: mainmodel.log for local run and log/node#.log for MPI run]\n")
		sys.stdout.write("   --log-level=DEBUG|INGO|WARNING|ERROR|CRITICAL|\n")
		sys.stdout.write("                                  : sets log level [default: DEBUG or INFO]\n")
		sys.stdout.write("   --no-run                       : prevents the simulation. This option allows analysis results of simulation without\n")
		sys.stdout.write("                                    re-simulation. You can make an rsults analysing in the Python whithout NEURON:\n")
		sys.stdout.write("                                     python mainmodel.py --no-run --graphs\n")
		sys.stdout.write("   --mod-compiler=compiler_prog   : set compiler program for NEURON mod files [default: nenivmodl]\n")
		sys.stdout.write("   --preset-only                  : makes preset(preprocessing) procedures and exit\n")
		sys.stdout.write("                                    preset totally sets network (generates networkfile), copies all modules to root\n")
		sys.stdout.write("                                    directory and calculate \'fingerprint\' of model. After preset configuration file\n")
		sys.stdout.write("                                    can NOT be modified! Use --preset-only option to prepare the job for NSG portal\n")
		sys.stdout.write("   --non-parallel                 : prevents parallel running\n")
		sys.stdout.write("   --non-threads                  : prevents using multithreading\n")
		sys.stdout.write("   --collect                      : makes and index of all recorded cells and writes an index and all recordings in one file\n")
		sys.stdout.write("                                    if you run --graphs or other post-processing procedures, collection will be made\n")
		sys.stdout.write("                                    automatically\n")
		sys.stdout.write("   --graphs                       : reads GRAPHS section of configuration file or alternative configuration file \n")
		sys.stdout.write("                                    (see --config-exp) to draw or/and show results of simulations\n")
		sys.stdout.write("   --config-exp=another_configuration_file\n")
		sys.stdout.write("                                  : expands configuration file and alters all post-processing options.\n")
		sys.stdout.write("                                    Use this option for multiple analyses of simulation results. This option does not alter\n")
		sys.stdout.write("                                    main configuration file and model fingerprint (so do not trigger simulation) in preset\n")
		sys.stdout.write("                                    and simulation stages but reset sections [GRAPHS], [VIEW] and so on in post-processing.\n")
		sys.stdout.write("                                    This expands all sections in the main configuration, so be careful with section/option\n")
		sys.stdout.write("                                    duplication, this will raise and error\n")
		#sys.stdout.write("   
		#sys.stdout.write("                                    \n")
		sys.stdout.write("\n")
		exit(0)

#Hook
config["CONF"]["parallel"] &= config["CONF"]["mpi"]

pycore = os.path.basename(sys.argv[0])
if not "GENERAL" in config:
	config["GENERAL"] = {}
if pycore == 'nrniv':
	if config["CONF"]["parallel"]:
		#DB>>>
		#print "X point"
		#<<<DB
		try:
			from mpi4py import MPI
		except:
			from neuron import h
			pc = h.ParallelContext()
			if int(pc.nhost()) > 1:
				sys.stderr.write("I need mpi4py to run NEURON+MPI")
				sys.exit(1)
		#DB>>>
		#print "Y point"
		#<<<DB
		from neuron import h
		pc = h.ParallelContext()
		config["GENERAL"]["system"]		= 'nrn'
		config["GENERAL"]["NODERANGE"]	= range(int(pc.nhost()))
		config["GENERAL"]["NODEID"]		= int(pc.id())
		config["GENERAL"]["NODETOTALS"]	= int(pc.nhost())
		config["CONF"]["PC"]			= pc
	else:
		from neuron import h
		pc = h.ParallelContext()
		config["GENERAL"]["system"]		= 'nrn'
		config["GENERAL"]["NODERANGE"]	= range(1)
		config["GENERAL"]["NODEID"]		= 0
		config["GENERAL"]["NODETOTALS"]	= 1

else:
	config["GENERAL"]["system"]		= 'python'
	#try:
		#from mpi4py import MPI
		#cw = MPI.COMM_WORLD
		#config["GENERAL"]["NODERANGE"]	= range(int(cw.size))
		#config["GENERAL"]["NODEID"]		= int(cw.rank)
		#config["GENERAL"]["NODETOTALS"]	= int(cw.size)
	#except:
	config["GENERAL"]["NODERANGE"]	= range(1)
	config["GENERAL"]["NODEID"]		= 0
	config["GENERAL"]["NODETOTALS"]	= 1

if config["GENERAL"]["NODETOTALS"] == 1:
	config["GENERAL"]["NODERANGE"]	= range(1)
	config["CONF"]["parallel"]	= False
	if config["CONF"]["log"] == None:
		config["CONF"]["log"] = 'mainmodel.log' 
else:
	if config["CONF"]["log"] == None:
		config["CONF"]["log"] = 'log/node%03d.log'%config["GENERAL"]["NODEID"]

try : exec 'loglevel = logging.'+config["CONF"]["log-level"]
except BaseException as e:
	sys.stderr.write("Couldn't setup log level to %s. Using default 'DEBUG'"%config["CONF"]["log-level"])
	loglevel = logging.DEBUG

logging.basicConfig(filename=config["CONF"]["log"],format='%(asctime)s:%(module)-10s%(levelname)-8s:%(message)s', level=loglevel)
	
logging.info("#############################")
logging.info("STARTING AT NODE %03d OF RANGE %03d"%(config["GENERAL"]["NODEID"],config["GENERAL"]["NODETOTALS"]))
logging.info("#############################")
logging.info("NEURON OR PYTHON:")
logging.info(" > I run on %s"%pycore)
if pycore == 'nrniv':
	logging.info( " > PYTHON CORE is NEURON")
else:
	logging.info(" > PYTHON CORE is Python")
if config["GENERAL"]["NODETOTALS"] == 1:
	logging.info( " > Only one host - turn off parallelization ...")
else:
	logging.info( " > I'm node %03d of RANGE: %03d"%(config["GENERAL"]["NODEID"],config["GENERAL"]["NODETOTALS"]) )


logging.info("READ CONFIG FILE \'%s\':"%config["CONF"]["file"])
config["GENERAL"]["CONFIGHASH"]		= hashsum(config["CONF"]["file"])
logging.info(" > Checksum %s"%config["GENERAL"]["CONFIGHASH"])

logging.debug("Reading all configuration sections except: {}".format(["GENERAL","AUDITORY NERVE","STIMULI","POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","CELLS","SIMULATION","GRAPHS","VIEW","STAT"]))
config = confreader( config["CONF"]["file"], nspace=config, skip = ["GENERAL","AUDITORY NERVE","STIMULI","POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","CELLS","SIMULATION","GRAPHS","VIEW","STAT"] )
if config == {} or config == None:
	logging.error("Couldn't read all sections except {} from config file '{}' ".format(["GENERAL","AUDITORY NERVE","STIMULI","POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","CELLS","SIMULATION","GRAPHS","VIEW","STAT"],config))
	pcexit(1)
logging.info(" > DONE")


logging.debug("Reading configuration for sections: {}".format(["GENERAL","AUDITORY NERVE","STIMULI","CELLS"]))
config = confreader( config["CONF"]["file"], nspace=config, sections = ["GENERAL","AUDITORY NERVE","STIMULI","CELLS"] )
if config == {} or config == None:
	logging.error("Couldn't read section {} from config file '{}' ".format(["GENERAL","AUDITORY NERVE","STIMULI","CELLS"],config))
	pcexit(1)
logging.info(" > DONE")

config = checkgeneralsettings( config )
if config == None: pcexit(1)

#DB>>
#exit(0)
#<<DB

logging.info("ADDING THE PATHS:")
if type(config["GENERAL"]["pyextrapath"]) is str:
	extrapath = [  config["GENERAL"]["pyextrapath"] ]
else:
	extrapath = list( config["GENERAL"]["pyextrapath"]  )
logging.info(" > Python extrapath: %s"%str(extrapath))
try:	sys.path = [ sys.path[0] ] + extrapath + sys.path[1:]
except:pass


config = presetstimuli( config )
if config == None or config == {} :
	logging.error("ABBORT!")
	pcexit(1)

logging.debug("Reading configuration for sections: {}".format(["POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","SIMULATION"]))
config = confreader( config["CONF"]["file"], nspace=config, sections = ["POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","SIMULATION"] )
if config == {} or config == None:
	logging.error("Couldn't read section {} from config file '{}' ".format(["POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","SIMULATION"],config))
	pcexit(1)
logging.info(" > DONE")

config["GENERAL"]["NETWORKHASH"]=""
for section in ["GENERAL","AUDITORY NERVE","STIMULI","POPULATIONS","SYNAPSES","CONNECTIONS","RECORD","CELLS","SIMULATION"]:
	config["GENERAL"]["NETWORKHASH"] += config[section]["__:hash:__"]

if config["GENERAL"]["NODEID"] == 0:
	config = presetnetwork( config )
	if config == None or config == {} :
		logging.error("ABBORT!")
		pcexit(1)
	config = presetmodules( config )
	if config == None or config == {} :
		logging.error("ABBORT!")
		pcexit(1)
else:
	if not 'networkfilename' in config["GENERAL"]:
		logging.error("There is no networkfilename option in GENERAL section ")
		pcexit(1)
	attemps_cnt = 0
	while True:
		if os.access(config["GENERAL"]['networkfilename'],os.R_OK):
			with open(config["GENERAL"]['networkfilename'],"rb") as fd:
				hsum = pickle.load(fd)
			if hsum == config["GENERAL"]["NETWORKHASH"] :
				logging.info(" > Presetting complete")
				break
			else:
				logging.warning(" > Hash finger print isn't match. Wait!")
		else:
			logging.warning(" > Couldn't find network file %s. Wait!"%config["GENERAL"]['networkfilename'])
		time.sleep(5)
		attemps_cnt += 1
		if attemps_cnt > 12:
			logging.error("Stuck more than 1 min!")
			pcexit(1)

logging.debug("CHECK CELL CLASSES")
if not "CellClasses" in config["CELLS"]:
	logging.error('Cannot find "CellClasses" option in the CELLS option')
	pcexit(1)
if type (config["CELLS"]["CellClasses"]) is str:
	config["CELLS"]["CellClasses"] = [ config["CELLS"]["CellClasses"] ]
if not( type (config["CELLS"]["CellClasses"]) is tuple or type (config["CELLS"]["CellClasses"]) is list):
	logging.error('Cannot find "CellClasses" option in the CELLS section')
	pcexit(1)
for cellclass in config["CELLS"]["CellClasses"]:
	if not cellclass in config["CELLS"]:
		logging.error('Cannot find cell class {} option in the CELLS section'.format(cellclass))
		pcexit(1)
	if not type (config["CELLS"][cellclass]) is str:
		logging.error('Wrong type of cell class {} option in the CELLS section'.format(cellclass))
		pcexit(1)
	if config["GENERAL"]["system"] == 'nrn' :
		try:
			exec config["CELLS"][cellclass]+" as {}".format(cellclass)
		except BaseException as e:
				logging.error("Coudn't import cell {}".format(cellclass))
				logging.error("Exception {}".format(e))
				pcexit(1)
		logging.info(" > {} is successfully imported".format(cellclass) )
	else:
		logging.info(" > Couldn't check CellClass {}: My Python CORE is {}".format(cellclass,config["GENERAL"]["system"]))
		
if config["CONF"]["preset"] : pcexit(0)

########################################################################
#                          SIMULATOR!!!!!!                             #
#                                                                      #
########################################################################

#logging.debug("Reading configuration for sections: {}".format(["SIMULATION"]))
#config = confreader( config["CONF"]["file"], nspace=config, sections = ["SIMULATION"] )
#if config == {} or config == None:
	#logging.error("Couldn't read section {} from config file '{}' ".format(["SIMULATION"],config))
	#pcexit(1)
#logging.info(" > DONE")


if config["CONF"]["run"]:
	if config["GENERAL"]["system"] == 'python' :
		logging.error("Cannot run simulator without NEURON")
		logging.info("My enviropment: %s"%os.path.basename(sys.argv[0]))
		pcexit(1)
	logging.info("############## SIMULATOR ###############")

	#Need for NSG portal
	h.load_file("stdgui.hoc")


	cells,synapses,netcons,recorders = [], [], [], []
	stimdurations = []

	logging.info("CREATE A NETWORK:")
	mygids	= []
	cellidx	= []
	mypops	= {}
	mindelay = None
	with open(config["GENERAL"]['networkfilename'],"rb") as fd:
		pickle.load(fd) #checksum
		while True:
			try: obj = pickle.load(fd)
			except: break
			if obj[0] == "p":
				if config["CONF"]["parallel"]:
					popobj = config["POPULATIONS"][obj[1]]
					if  popobj[0] == None: popobj[0] = config["GENERAL"]["NODETOTALS"]
					if type(popobj[0]) is int:
						if popobj[0] != config["GENERAL"]["NODEID"]: continue
						#if it my and only my population, I have to add all of tham
						mypops[ obj[1] ] = [len(mygids)]
						mygids += [ a[0] if type(a) is list or type (a) is tuple else a for a in obj[2] ]
						if (len(mygids)-1) > mypops[ obj[1] ][0]:
							mypops[ obj[1] ].append(len(mygids)-1)
					elif type(popobj[0]) is tuple or type(popobj[0]) is list :
						if not config["GENERAL"]["NODEID"] in popobj[0]: continue
						idx		= popobj[0].index(config["GENERAL"]["NODEID"])
						total	= len(popobj[0])
						if idx >= len(obj[2]): continue
						mypops[ obj[1] ] = [len(mygids)]
						mygids += [ a[0] if type(a) is list or type (a) is tuple else a for a in obj[2][idx::total] ]
						if (len(mygids)-1) > mypops[ obj[1] ][0]:
							mypops[ obj[1] ].append(len(mygids)-1)
				else:
					mypops[ obj[1] ] = [len(mygids)]
					mygids += [ a[0] if type(a) is list or type (a) is tuple else a for a in obj[2] ]
					if (len(mygids)-1) > mypops[ obj[1] ][0]:
						mypops[ obj[1] ].append(len(mygids)-1)
				logging.debug(" > add population %s GIDs %s"%(obj[1],str(obj[2])))
			elif obj[0] == 'md':
				mindelay = obj[1]
				logging.debug(" > minimal delay is {}".format(mindelay))
			elif obj[0] == 'n':
				if not obj[1] in mygids: continue
				try : exec 'cells.append( '+obj[3]+' )'
				except BaseException as e:
					logging.error("Coudn't create cell gid: %d %s"%(obj[1],obj[3]))
					logging.error("Exception %s"%e)
					pcexit(1)
				cellidx.append( obj[1] )
				logging.debug(" > create an neuron GID %d"%obj[1])
			elif obj[0] == 'c':
				if not obj[1] in mygids: continue
				idx = cellidx.index(obj[1])
				cell = cells[ idx ]
				try : exec "synapse = " + obj[2]
				except BaseException as e:
					logging.error("Coudn't create synapse gid: %d %s"%(obj[1],obj[2]))
					logging.error("      %s"%e)
					pcexit(1)
				for name in obj[3]:
					try : exec "synapse."+name+" = "+str(obj[3][name])
					except BaseException as e:
						logging.error("Coudn't setup synaptic parameter gid: %d, synapse: %s, parameter:%s"%(obj[1],obj[2],name))
						logging.error("      %s"%e)
						pcexit(1)
				synapses.append(synapse)
				for pregid,gmax,delay in  obj[4]:
					nc = pc.gid_connect(pregid,synapse)
					nc.weight[0]	= gmax
					nc.delay	= delay
					netcons.append(nc)
				logging.debug(" > create a synapse GID %d, syn %s, param %s, connects %s"%(obj[1],obj[2],str(obj[3]),str(obj[4])))
			elif obj[0] == 'rc':
				if not obj[1] in mygids: continue
				idx  = cellidx.index(obj[1])
				cell = cells[ idx ]
				vect = h.Vector()
				try : exec "vect.record(cell." + obj[2]+")"
				except BaseException as e:
					logging.error("Coudn't set up recorder gid %d: %s"%(obj[1],obj[2]))
					logging.error("      %s"%e)
					pcexit(1)
				recorders.append( [obj[3],obj[1],obj[2],vect] )
				logging.debug(" > create a recorder rec %s, GId %d, cmd %s"%(obj[3],obj[1],obj[2]) )
			elif obj[0] == "sd":
				stimdurations += obj[1:]
				logging.debug(" > add stimuli duration %s"%str(obj[1:]))
	logging.info(" > DONE")
	if mindelay == None:
		logging.error("Minimal delay isn't set")
		pcexit(1)
	if not config["CONF"]["parallel"]:
		if config["CONF"]["threads"] > 0:
			if 'threads' in config["SIMULATION"] and type(config["SIMULATION"]['threads']) is int:
				config["CONF"]["threads"] = config["SIMULATION"]['threads']
			pc.nthread(config["CONF"]["threads"])
			logging.info("Local simulation with %d threads :)"%config["CONF"]["threads"])
		else:
			logging.info("Local simulation with one thread :(")
	if config["GENERAL"]["NODEID"] == 0:
		dummysec = h.Section()
		rect = h.Vector( sec=dummysec)
		rect.record(h._ref_t,sec=dummysec)
	for stim,stimdur in map(None,config["STIMULI"]['stimuli'],stimdurations):
		if type(stim) is str:
			if not stim in config["STIMULI"]:
				logging.error("couldn't find '%s' in STIMULI section"%stim)
				pcexit(1)
			stimobj = config["STIMULI"][stim]
			stimname = stim
		else:
			stimobj = stim
			for names in config["STIMULI"]:
				if config["STIMULI"][names] == stim:
					stimname = names
					break
		if stimdur[0] != stimname:
			logging.error("Different stimuli at same time in preset:\'%s\' in config:\'%s\'"%(stimdur[0],stimname) )
			pcexit(1)
		stimdur = stimdur[1]
		logging.info("STIMULUS:%s[dur:%g]"%(stimname,stimdur))
		for inputs in stimobj[2]:
			if not inputs[0] in mypops: continue
			for cellidx in mypops[inputs[0]]:
				try:
					exec "cells[cellidx]."+inputs[1]+"(\'"+stimobj[0]+"\')"
					logging.debug(" > Population %s has read file"% inputs[0])
				except BaseException as e:
					logging.error("Population %s can not read stimulus \'%s\':%s"%(inputs[0],stimobj[0],e) )
					pcexit(1)
		h.tstop = stimdur
		for opt in config["SIMULATION"]:
			if opt[:2] == "h.":
				try:
					exec opt+"={}".format(config["SIMULATION"][opt])
				except BaseException as e:
					logging.error("Couldn't execute \'%s\':%s"%(opt+"={}".format(config["SIMULATION"][opt]),e) )
					pcexit(1)
			
		if config["CONF"]["parallel"]:
			pc.set_maxstep(mindelay)
			h.stdinit()
			pc.psolve(h.tstop)
		else:
			h.stdinit()
			h.run()
		
		logging.debug(" > record to %s"%stimobj[3])
		with open(stimobj[3]+"%03d"%config["GENERAL"]["NODEID"],"wb") as fd:
			pickle.dump(['h',config["GENERAL"]["NETWORKHASH"],config["GENERAL"]["NODEID"],config["GENERAL"]["NODETOTALS"]],fd)
			if config["GENERAL"]["NODEID"] == 0:
				pickle.dump(["time",np.array(rect)],fd)
			for cell in cells:
				cell.save(fd)
			for rec in recorders:
				pickle.dump(["rec"]+rec[:3]+[np.array(rec[-1])],fd)

else:
	logging.info("==== SKIP THE SIMULATION ====")


########################################################################
#                     VISUALIZATION AND ANALYSES                       #
#                                                                      #
########################################################################

if config["GENERAL"]["system"] == 'nrn' and config["GENERAL"]["NODEID"] != 0: pcexit(0)
if config["GENERAL"]["system"] == 'nrn' and config["CONF"]["run"]:
	del	cells,synapses,netcons,recorders
	del stimdurations 
	del mygids, cellidx, mypops

if  config["CONF"]["collect"] or \
	config["CONF"]["graphs"]  or \
	config["CONF"]["view"]    or \
	config["CONF"]["stat"]:
	config = collect(config)
	if config == {} or config == None: 
		logging.error("ABBORT!")
		pcexit(1)
else: pcexit(0)

logging.debug("Reading configuration for sections: {}".format(["GRAPHS","VIEW","STAT"]))
config = confreader( config["CONF"]["file"], nspace=config, sections = ["GRAPHS","VIEW","STAT"] )
if config == {} or config == None:
	logging.error("Couldn't read section {} from config file '{}' ".format(["GRAPHS","VIEW","STAT"],config))
	pcexit(1)
logging.info(" > DONE")

if config["CONF"]["conf-exp"] != None:
	logging.info("Read expation for graphs, stat and view from %s"%config["CONF"]["conf-exp"])
	# Add here cleaning for all section in configuration file, which active
	# in processing of simulation result: 'GRAPHS', 'VIEW' and so on......
	if 'GRAPHS' in config: config['GRAPHS'] = {}
	if 'STAT'   in config: config['STAT'] = {}
	#if 'VIEW'   in config: config['VIEW'] = {}
	config = confreader( config["CONF"]["conf-exp"], nspace=config )
	if config == {} or config == None:
		logging.error("ABBORT!")
		pcexit(1)

if config["CONF"]["graphs"] and 'GRAPHS' in config:
	from tools.graphs import *
	logging.debug("Default Module \'tools.graphs\' has been imported successfully")
	if 'import' in config['GRAPHS'] :
		if type(config['GRAPHS']['import']) is str:
			config['GRAPHS']['import'] = [ config['GRAPHS']['import'] ]
		for cmd in config['GRAPHS']['import']:
			try : exec cmd
			except BaseException as e:
				logging.error("Coudn't import module %s: %s"%(cmd,e) )
				pcexit(1)
			logging.debug("Module \'%s\' has been imported successfully"%cmd)
	if 'Figures' in config['GRAPHS'] :
		if type(config['GRAPHS']['Figures']) is str:
			config['GRAPHS']['Figures'] = [config['GRAPHS']['Figures']]
		for fig in config['GRAPHS']['Figures']:
			if type(fig) is str:
				figname = fig
				if not fig in config['GRAPHS'] :
					logging.error("couldn't find Figure '%s' in GRAPHS section"%fig)
					pcexit(1)
				figobj = config['GRAPHS'][fig]
			else:
				figobj = fig
				figname = None
				for fxg in config['GRAPHS']:
					if config['GRAPHS'][fxg] == figobj: figname = fxg
				if figname == None:
					logging.error("couldn't find Figure with same object %s in GRAPHS section"%fig)
					pcexit(1)
			if type(figobj) is str:
				figobj = [ figobj ]
			for cmd in figobj:
				logging.debug("Graph > execute %s"%cmd)
				try:
					exec cmd
				except BaseException as e:
					logging.error("Coudn't execute %s: %s"%(cmd,e) )
					pcexit(1)
			logging.info("Figure %s is done"%figname)

if config["CONF"]["stat"] and 'STAT' in config:
	from tools.stat import *
	logging.debug("Default Module \'tools.stat\' has been imported successfully")
	if 'import' in config['STAT'] :
		config['STAT']['import'] = [ config['STAT']['import'] ]
		for cmd in config['STAT']['import']:
			try : exec cmd
			except BaseException as e:
				logging.error("Coudn't import module %s: %s"%(cmd,e) )
				pcexit(1)
			logging.debug("Module \'%s\' has been imported successfully"%cmd)
	if not 'file' in config['STAT']:
		logging.error("there is no file option in STAT option")
		pcexit(1)
	if not 'delimiter' in config['STAT']:
		config['STAT']['delimiter'] = '\t'
		logging.warning(" > STAT section has not delimiter option. Set it up by default: TAB SYMBOL")
	if not 'records' in config['STAT']:
		logging.error("Coudn't find option records in STAT section" )
		pcexit(1)
	if type(config['STAT']['records']) is str:
		config['STAT']['records'] = [ config['STAT']['records'] ]
	if not (type(config['STAT']['records']) is list or type(config['STAT']['records']) is tuple):
		logging.error("Wrong type of records option in STAT section" )
		pcexit(1)
	line = "ID"
	for rec in config['STAT']['records']: line += config['STAT']['delimiter']+rec
	line += '\n'
	with open(config['STAT']['file'],'a') as fd: fd.write(line)
	line = "{}".format(config["GENERAL"]["NETWORKHASH"])
	for rec in config['STAT']['records']:
		if rec in config['STAT']:
			logging.debug("STAT > execute "+"stat_ret="+config['STAT'][rec])
			try : exec "stat_ret="+config['STAT'][rec]
			except BaseException as e:
				logging.error("Couldn't execute command {}: {}".format("stat_ret="+config['STAT'][rec],e) )
				pcexit(1)
			line += config['STAT']['delimiter']+"{}".format(stat_ret)
		else:
			logging.warning("Couldn't find {} option in STAT option, try to execute just option value") 
			logging.debug("STAT > execute "+"stat_ret="+rec)
			try : exec "stat_ret="+rec
			except BaseException as e:
				logging.error("Couldn't execute command {}: {}".format("stat_ret="+rec,e) )
				pcexit(1)
			line += config['STAT']['delimiter']+"{}".format(stat_ret)
	line += '\n'
	with open(config['STAT']['file'],'a') as fd: fd.write(line)
	logging.info("STATISTICS is done")
pcexit(0)
