"""
Preset procedure for configuration
"""
import sys,os, hashlib, types, glob
try:
	import cPickle as pickle
except:
	import pickle
import logging,time
import numpy as np


def checkgeneralsettings(config):
	logging.info("CHECK GENERAL SECTION:")
	if not "GENERAL" in config :
		logging.error("Couldn't find GENERAL section")
		return None
	if not 'networkfilename' in config["GENERAL"]:
		logging.error("Couldn't find network filename in GENERAL section")
		return None
	if not "pyextrapath" in config["GENERAL"]:
		logging.error("Couldn't find py extantion path in GENERAL section")
		return None
	if not "nhcell" in config["GENERAL"]:
		logging.error("Couldn't find nhcell in GENERAL section")
		return None
	if not type(config["GENERAL"]["nhcell"]) is int:
		logging.error("Wrong type of nhcell paramter in GENERAL section")
		return None
	if not "freqrange"  in config["GENERAL"]:
		logging.error("Couldn't find frequencies range in GENERAL section")
		return None
	if not (type(config["GENERAL"]["freqrange"]) is list or type(config["GENERAL"]["freqrange"]) is tuple):
		logging.error("Wrong type of freqrange paramter in GENERAL section")
		return None
	if len(config["GENERAL"]["freqrange"]) != 2:
		logging.error("Wrong size of freqrange paramter in GENERAL section")
		return None
	if not ( type(config["GENERAL"]["freqrange"][0]) is int or type(config["GENERAL"]["freqrange"][0]) is float ) and \
		    ( type(config["GENERAL"]["freqrange"][1]) is int or type(config["GENERAL"]["freqrange"][1]) is float ):
		logging.error("Wrong size of freqrange paramter in GENERAL section")
		return None
		
	if not "nfibperhcell" in config["GENERAL"]:
		logging.error("Couldn't find nfibperhcell in GENERAL section")
		return None
	if not type(config["GENERAL"]["nfibperhcell"]) is int:
		logging.error("Wrong type of nfibperhcell paramter in GENERAL section")
		return None

	if not "fibersproportion"  in config["GENERAL"]:
		logging.error("Couldn't find fiber types proportions in GENERAL section")
		return None
	if not (type(config["GENERAL"]["fibersproportion"]) is list or type(config["GENERAL"]["fibersproportion"]) is tuple):
		logging.error("Wrong type of fibersproportion paramter in GENERAL section")
		return None
	if len(config["GENERAL"]["fibersproportion"]) != 3:
		logging.error("Wrong size of fibersproportion paramter in GENERAL section")
		return None
	if not	( type(config["GENERAL"]["fibersproportion"][0]) is int or type(config["GENERAL"]["fibersproportion"][0]) is float ) and \
		    ( type(config["GENERAL"]["fibersproportion"][1]) is int or type(config["GENERAL"]["fibersproportion"][1]) is float ) and \
		    ( type(config["GENERAL"]["fibersproportion"][2]) is int or type(config["GENERAL"]["fibersproportion"][2]) is float ):
		logging.error("Wrong size of fibersproportion paramter in GENERAL section")
		return None
	
	if not "distribution" in config["GENERAL"]:
		config["GENERAL"]["distribution"] = 'log10'
	config["GENERAL"]["uniform"] = (config["GENERAL"]["distribution"] == 'uniform')
	logging.info(" > DONE")
	return config

def presetstimuli(config):
	def stimgenerate(config,stim):
		cmd = config["STIMULI"]['prog']+" "+config["STIMULI"][stim][1]['stimtype']
		for param in config["STIMULI"][stim][1]:
			if param == 'stimtype' or param == "frequency-range" or param == "number-hair-cells": continue
			if param == 'fiber-per-hcell' or param == "portion-types" : continue
			if param == 'inputfile' : cmd += " "+str(+config["STIMULI"][stim][1][param])
			cmd += " --"+param+"="+str(+config["STIMULI"][stim][1][param])
		cmd += " --frequency-range %g %g"%tuple(config["GENERAL"]["freqrange"])
		cmd += " --number-hair-cells %d "%(config["GENERAL"]["nhcell"])
		cmd += " --fiber-per-hcell %d"%(config["GENERAL"]["nfibperhcell"])
		cmd += " --portion-types %f %f %f"%tuple(config["GENERAL"]["fibersproportion"])
		cmd += " -s"
		if config["GENERAL"]["uniform"]:
			cmd += " -u"
		cmd += " "+config["STIMULI"][stim][0]
		logging.info(" > Regenerate by command: %s"%(cmd))
		return os.system(cmd)

	logging.info("CHECK STIMULI FILES:")
	if not "STIMULI" in config:
		logging.error("Couldn't find STIMULI section")
		return None
	if not 'stimuli' in config["STIMULI"]:
		logging.error("Couldn't find 'stimuli' set in the STIMULI section")
		return None
	if type(config["STIMULI"]['stimuli']) is str:
		config["STIMULI"]['stimuli'] = [ config["STIMULI"]['stimuli'] ]
	if not (type(config["STIMULI"]['stimuli']) is list or type(config["STIMULI"]['stimuli']) is tuple):
		logging.error("Wrong type of stimuli paramter in the STIMULI section")
		return None
	if not 'prog' in config["STIMULI"]:
		logging.warning("use prog by default")
		config["STIMULI"]['prog'] = "./an-response-generator"

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
			
		if not os.access(stimobj[0],os.R_OK):
			logging.warning("Couldn't find stimulus file %s"%(stimobj[0]))
			if stimgenerate(config,stim): return None
			with open(stimobj[0]) as fd:
				params	=  pickle.load(fd)
			if not 'stimdur' in params :
				logging.error("couldn't find stimulus duration in %s"%stimobj[0])
				return None
			stimobj.append(params['stimdur'] * 1000.)
		else:
			with open(stimobj[0]) as fd:
				params	=  pickle.load(fd)
			if config["GENERAL"]["uniform"] != params["uniform"]:
					if stimgenerate(config,stim): return None
			elif tuple(config["GENERAL"]["freqrange"]) != tuple(params["frequency-range"]):
				if stimgenerate(config,stim): return None
			elif params["number-hair-cells"] != config["GENERAL"]["nhcell"]:
				if stimgenerate(config,stim): return None
			elif params["fiber-per-hcell"]  != config["GENERAL"]["nfibperhcell"]:
				if stimgenerate(config,stim): return None
			elif tuple(params["portion-types"])  != tuple(config["GENERAL"]["fibersproportion"]):
				if stimgenerate(config,stim): return None
			elif not 'stimdur' in params :
				logging.error("couldn't find stimulus duration in %s"%stimobj[0])
				return None
			stimobj.append(params['stimdur'] * 1000.)

			for param in stimobj[1]:
				if stimobj[1][param] != params[param]:
					if stimgenerate(config,stim): return None
					break
			
			else: logging.info( " > %s [dur: %f ms] .... OK"%(stimobj[0],stimobj[-1]))
		if not 'stimdur' in config["CONF"]:
			config["CONF"]['stimdur'] = ["sd"]
		config["CONF"]['stimdur'].append((stimname,stimobj[-1]))
	return config

def hashsum(filename):
	m = hashlib.sha256()
	with open(filename,'rb') as f: 
		for chunk in iter(lambda: f.read(128*m.block_size), b''): 
			m.update(chunk)
	return m.hexdigest()

def resolve2object(robj, xgid, ygid=None):
	if type(robj) is str or type(robj) is int \
	or type(robj) is float  or type(robj) is bool : return robj
	if type(robj) is tuple or type(robj) is list:
		return [ resolve2object(subobj,xgid,ygid) for subobj in robj ]
	if type(robj) is dict:
		retobj = {}
		for subobj in robj:
			retobj[subobj] = resolve2object(robj[subobj],xgid,ygid)
		return retobj
	if type(robj) is types.LambdaType and robj.__name__ == '<lambda>':
		if ygid == None:
			return robj(xgid)
		else:
			return robj(xgid,ygid)
	return None

def popoffcet(gid,base,total):
	if total < 2: return 0
	return float(gid-base)/float(total - 1 )

def populationpreset( config ):
	gid = 0
	if not "POPULATIONS" in config:
		logging.error("couldn't find POPULATION section")	
		return None
	
	logging.info("PREPROCESSING POPULATIONS:")
	sys.stderr.write("PREPROCESSING POPULATIONS:\n")
	for population in config["POPULATIONS"]:
		totalcells = reduce(lambda x,y: x+y[1],config["POPULATIONS"][population][1:],0)
		popbasegid = gid
		pop =[]
		gids = []
		for cid in xrange( totalcells ):
			portion = np.zeros(len(config["POPULATIONS"][population]) - 1)
			for tcell,tid in map(None,config["POPULATIONS"][population][1:],xrange(len(config["POPULATIONS"][population]) - 1)):
				if type(tcell[4]) is types.LambdaType and tcell[4].__name__ == '<lambda>':
					portion[tid] = tcell[4]( popoffcet(gid,popbasegid,totalcells) )
				elif type(tcell[4]) is float or type(tcell[4]) is int:
					portion[tid] = float(tcell[4])
				else:
					logging.error("wrong distribution function in population:%s cell type:%s"%(population,tcell[0]))
					return None
			portion /= np.sum(portion)
			portion[1:] += portion[:-1]
			rnd = np.random.rand()
			ids = np.where( (portion-rnd) >= 0.)[0][0] + 1
			tcell = config["POPULATIONS"][population][ids]
			cls = tcell[0]+"("+reduce(lambda x,y:x+"%s=%s, "%(y,str(resolve2object(tcell[3][y],popoffcet(gid,popbasegid,totalcells)))),tcell[3],'')+"gid=%d, pc=pc)"%gid
			#pop.append( [ 'n', population, gid - popbasegid, gid, cls] )			
			pop.append( [ 'n', gid, ids,cls] )
			sys.stderr.write(".")
			if not bool(cid%50):
				sys.stderr.write("\r                                                   \r")
			if tcell[2] == 1:
				gids.append(gid)
			else:
				gids.append( (gid,gid+tcell[2]-1) )
			gid += tcell[2]
		config["POPULATIONS"][population].append( (popbasegid,gid) )
		with open(config["GENERAL"]['networkfilename'],"ab") as fd:
			##write all basi id of this populstion first!!!!!
			pickle.dump(['p',population,gids],fd)
			for p in pop:
				pickle.dump(p,fd)
	sys.stderr.write("\r#           DONE            #                                \n")
	logging.info(" > DONE")
	return config

def synapticpreset(config):
	if not 'SYNAPSES' in config : return config
	for syn in config['SYNAPSES']:
		if 'name' in config['SYNAPSES'][syn]:
			logging.error("Synapses:%s has variable \'name\'"%(syn))
			return None
		config['SYNAPSES'][syn]['name']=syn
		for prm in config['SYNAPSES'][syn]:
			if type(config['SYNAPSES'][syn][prm]) is types.LambdaType and config['SYNAPSES'][syn][prm].__name__ == '<lambda>':
				logging.error("lambda function was defined in Synapses:%s "%(syn))
				return None
	return config

def congen(config):
	if not 'CONNECTIONS' in config :
		logging.warning("Couldn't find CONNECTIONS section.... Not sure that skipping is good idea")
		return config
	logging.info("PREPROCESSING CONNECTIONS:")
	sys.stderr.write("PREPROCESSING CONNECTIONS:\n")
	### Preset connections names
	mindelay= None
	for con in config['CONNECTIONS']:
		conobj = config['CONNECTIONS'][con]
		if len(conobj) != 10:
				logging.error("number of parameters for option %s in section CONNECTIONS are wrong"%con)
				return None
		if not type(conobj[0]) is str:
				logging.error("type of presynaptic population name for option %s in section CONNECTIONS is wrong"%con)
				return None
		if not conobj[0] in config["POPULATIONS"]:
				logging.error("coudn't find population %s for connection %s"%(conobj[0],con) )
				return None
		else:
			conobj[0] = config["POPULATIONS"][conobj[0]]
		if not type(conobj[1]) is str:
				logging.error("type of postsynaptic population name for option %s in section CONNECTIONS is wrong"%con )
				return None
		if not conobj[1] in config["POPULATIONS"]:
				logging.error("coudn't find population %s for connection %s"%(conobj[1],con) )
				return None
		else:
			conobj[1] = config["POPULATIONS"][conobj[1]]

		if not ( type(conobj[-1]) is str or type(conobj[-1]) is dict ):
				logging.error("type of synaptic parameter for option %s in section CONNECTIONS are wrong"%con )
				return None
		if type(conobj[-1]) is str:
			if not 'SYNAPSES' in config :
				logging.error("couldn't find SYNAPSES section" )
				return None
			if not conobj[-1] in config["SYNAPSES"]:
				logging.error("couldn't find synapse %s in SYNAPSES section"%(config['CONNECTIONS'][con][-1]) )
				return None
			conobj[-1] = config["SYNAPSES"][conobj[-1]]
	### Make temporal variables
		if conobj[2]:
			FROMH,TOH = conobj[1][-1]
			FROML,TOL = conobj[0][-1]
			presynpos = lambda hgid,lgid: popoffcet(lgid,FROML,TOL-FROML)
			possynpos = lambda hgid,lgid: popoffcet(hgid,FROMH,TOH-FROMH)
			getpregid = lambda hgid,lgid: lgid
			getposgid = lambda hgid,lgid: (hgid, hgid-FROMH)
			postlist  = [ [] for x in xrange(FROMH,TOH) ]
		else:
			FROMH,TOH = conobj[0][-1]
			FROML,TOL = conobj[1][-1]
			presynpos = lambda hgid,lgid: popoffcet(hgid,FROMH,TOH-FROMH)
			possynpos = lambda hgid,lgid: popoffcet(lgid,FROML,TOL-FROML)
			getpregid = lambda hgid,lgid: hgid
			getposgid = lambda hgid,lgid: (lgid, lgid-FROML)
			postlist  = [ [] for x in xrange(FROML,TOL) ]			
		conobj[3] = not conobj[3]
		for hgid in xrange(FROMH,TOH):
			syncnt = 0
			if type(conobj[4]) is types.LambdaType and conobj[4].__name__ == '<lambda>':
				totsyn = conobj[4](popoffcet(hgid,FROMH,TOH))
			elif type(conobj[4]) is float or type(conobj[4]) is int:
				totsyn = int(conobj[4])
			else:
				logging.error("number of connecction isn't integer for connection %s"%con )
				return None
			
			if conobj[3]:
				mask = [ False for x in range(FROML,TOL) ]
			while syncnt < totsyn:
				lgid = np.random.randint(FROML, high=TOL)
				if conobj[3] and mask[lgid-FROML]: continue
				x = presynpos(hgid,lgid)
				y = possynpos(hgid,lgid)
				if not conobj[5](x,y) : continue
				preid = getpregid(hgid,lgid)
				postid, postoff = getposgid(hgid,lgid)
				cond, delay =\
					float( resolve2object(conobj[6],x,y) ),\
					float( resolve2object(conobj[7],x,y) )
				if mindelay == None: mindelay = delay
				if mindelay > delay: mindelay = delay
				#if 'name' in conobj[9]:
					#pat = [ postid, conobj[9]['name'], conobj[8][0], conobj[8][1] ]
				#else:
					#pat = [ postid, resolve2object(conobj[9],x,y), conobj[8][0], conobj[8][1] ]
				if 'name' in conobj[9]:
					pat = [ postid, conobj[9]['name'], resolve2object(conobj[8][0],x,y), resolve2object(conobj[8][1],x,y) ]
				else:
					pat = [ postid, resolve2object(conobj[9],x,y), resolve2object(conobj[8][0],x,y), resolve2object(conobj[8][1],x,y) ]
				#print pat
				if len(postlist[postoff]) == 0:
					postlist[postoff].append( pat + [ [(preid,cond,delay)] ])
				for syntype in postlist[postoff]:
					if syntype[:-1] == pat :
						syntype[-1].append( (preid,cond,delay) )
						break
				else:
					postlist[postoff].append( pat + [ [(preid,cond,delay)] ])
 				syncnt += 1
				if conobj[3]: mask[lgid-FROML] = True
				sys.stderr.write(".")
				if not bool(syncnt%50):
					sys.stderr.write("\r%s                                                   \r"%con)
			sys.stderr.write("\r%s                                                   \r"%con)
		with open(config["GENERAL"]['networkfilename'],"ab") as fd:
			for pst in postlist:
				for syn in pst:
					if type(syn[1]) is str:
						syn[1] = conobj[-1]
					if not 'module' in syn[1]:
						logging.error("module name has not been found in a synapse option of connection: %s"%con)
						return None						
					cmd = syn[1]['module']+"(%g, sec=cell.%s)"%(syn[3],syn[2])
					prm = dict(syn[1])
					del prm['module']
					if "name" in prm:
						del prm["name"]
					pickle.dump(['c',syn[0],cmd,prm,syn[-1]],fd)
					
	with open(config["GENERAL"]['networkfilename'],"ab") as fd:
		pickle.dump(['md',mindelay],fd)
		logging.debug(" Minimal delay {}".format(mindelay))
	sys.stderr.write("\r#           DONE            #                                \n")
	logging.info(" > DONE")
	return config
	 
def networkgenerate(config):
	with open(config["GENERAL"]['networkfilename'],"wb") as fd:
		pickle.dump(config["GENERAL"]["CONFIGHASH"],fd)
		pickle.dump(config["CONF"]['stimdur'],fd)
	
	config = populationpreset(config)
	if config == None : return None
	config = synapticpreset(config)
	if config == None : return None
	config = congen(config)
	if config == None : return None
	config = presetrecord( config )
	if config == None : return None
	return config
	
def presetnetwork(config):
	if not 'networkfilename' in config["GENERAL"]:
		logging.error("There is no networkfilename option in GENERAL section ")
		return None		
	logging.info("NETWORK PRESET:")
	if not os.access(config["GENERAL"]['networkfilename'],os.R_OK):
		logging.warning(" > Couldn't find network file %s"%config["GENERAL"]['networkfilename'])
		logging.warning(" > REGENERATE!")
		return networkgenerate(config)
	with open(config["GENERAL"]['networkfilename'],"rb") as fd:
		hsum = pickle.load(fd)
	if hsum == config["GENERAL"]["CONFIGHASH"] and not config["CONF"]["preset"]:
		logging.info(" > Nothing to do !")
		return config
	if config["CONF"]["preset"] :
		logging.info(" > preset-only flag requires network regenerating")
	else:
		logging.warning(" > Configuration file and network file dosn't mutch")
		logging.warning(" > %s"%config["GENERAL"]['networkfilename'] )
		logging.warning(" > REGENERATE!")
	return networkgenerate(config)

def presetmodules(config):
	def scanANDcopy(path,localhash):
		recomp = False
		fllist = glob.glob(path+"/*.mod")
		for flname in fllist:
			sflname = os.path.basename(flname)
			if not sflname in localhash:
				os.system("cp %s %s"%(flname,sflname))
				logging.warning(" > There is no %s module in current directory. Copy it"%sflname)
				recomp = True
			elif hashsum(flname) != localhash[sflname]:
				os.system("cp %s %s"%(flname,sflname))
				logging.info(" > %s module was modified. Copy new version"%sflname)
				recomp = True
		return recomp

	logging.info("PRESET MODULES:")
	if not "CELLS" in config :
		logging.warning(" > There is nothing to preset")
		return config
	if not 'ModsCopy' in config["CELLS"]:
		logging.warning(" > There is no ModsCopy option in CELLS section")
		return config
	localhash={}
	fllist = glob.glob(os.getcwd()+"/*.mod")
	for flname in fllist:
		localhash[os.path.basename(flname)]=hashsum(flname)
	if type(config["CELLS"]['ModsCopy']) is str:
		pathlist = ( config["CELLS"]['ModsCopy'], )
	elif type(config["CELLS"]['ModsCopy']) is list or type(config["CELLS"]['ModsCopy']) is tuple:
		pathlist = config["CELLS"]['ModsCopy']
	else:
		logging.error("Wrong type of ModsCopy option in CELLS section")
		return None
	recomp = False
	for path in pathlist:
		recomp += scanANDcopy(path,localhash)
	if recomp and not config["CONF"]["preset"]:
		os.system(config["CONF"]["compiler"])
		time.sleep(5)
	logging.info(" > DONE")
	return config

def presetcellrec(rec, config):
	if type(rec) is str:
		recname = rec
		if not rec in config["RECORD"]:
			logging.error("There is no recorder %s in  RECORD section"%rec)
			return None
		rec = config["RECORD"][rec]
	else:
		for names in config["RECORD"]:
			if config["RECORD"][name] == rec:
				recname = names
				break
	if type(rec[0]) is str:
		if not rec[0] in config["POPULATIONS"]:
			logging.error("couldn't find population %s in  POPULATIONS section"%rec[0])
			return None
		rec[0] = config["POPULATIONS"][rec[0]]
	
	basegid,lastgid = rec[0][-1][0],rec[0][-1][1]
	total = lastgid-basegid
	reclist = [ ]
	if type(rec[1]) is int:
		if rec[1] >= total:
			logging.error("wrong index in recording %d. Index should be less than %d"%(rec[1],total))
			return None
		reclist.append( ['rc',rec[1]+basegid, tuple(rec[2:]), recname] )
	elif type(rec[1]) is list:
		for c in rec[1]:
			if c >= total:
				logging.error("wrong index in recording %d. Index should be less than %d"%(c,total))
				return None
			reclist.append( ['rc', c+basegid, tuple(rec[2:]) , recname] )
	elif type(rec[1]) is tuple:
		if rec[1][1] == None:
			maxcount = total
		else:
			maccount = rec[1][1]
		if len(rec[1]) < 3:
			step  = 1
		else:
			step = rec[1][2]
		for c in xrange(rec[1][0],maxcount,step):
			if c >= total:
				logging.error("wrong index in recording %d. Index should be less than %d"%(c,total))
				return None
			reclist.append( ['rc', c+basegid, tuple(rec[2:]) , recname] )
	with open(config["GENERAL"]['networkfilename'],"ab") as fd:
		for rec in reclist:
			if rec[2][2] == None:
				rec[2]="%s(%g)._ref_%s"%(rec[2][0],rec[2][1],rec[2][3])
			else:
				rec[2]="%s(%g).%s._ref_%s"%rec[2]
			pickle.dump(rec,fd)
	return config

def presetrecord(config):
	logging.info("PRESET RECORDERs:")
	if not 'RECORD' in config:
		logging.info(" > nothing to record")
		return config
	if 'cells' in config["RECORD"]:
		if not( type(config["RECORD"]['cells']) is tuple or type(config["RECORD"]['cells']) is list):
			logging.error("option cells in RECORD section MUST BE LIST!")
			return None
		for rec in config["RECORD"]['cells']:
			config = presetcellrec(rec, config)
			if config == None or config == {} :return None
		logging.info(" > DONE")
	else:
		logging.info(" > nothing record from cells")
	return config
