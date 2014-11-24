#! /usr/bin/env python
import sys, os, csv, glob
try:
	import cPickle as pickle
except:
	import pickle

import numpy as np
import numpy.random as rnd
import scipy as sc
import scipy.signal as ss
import logging

if __name__ == "__main__":
	homedir = os.path.dirname(sys.argv[0])
	sys.path.insert(0,homedir+"/tools")

import ZilanyCarney2009AN as an
import audiotools as at


class angen:
	def __init__(self):
		self.imported = True
	def check(self,filename,anconfig, stimparam, sectionchecksums):
		if not os.access(filename,os.R_OK):
			return self.generate(filename,anconfig, stimparam, sectionchecksums)
		with open(filename, "rb") as fd:
			try:
				sechash = pickle.load(fd)
				fparams = pickle.load(fd)
			except BaseException as e:
				logging.error("    > Cannot read from STIMULUS  file {}.".format(filename))
				return self.generate(filename,anconfig, stimparam, sectionchecksums)
		if sechash == sectionchecksums :
			logging.debug("    > STIMULUS file checksum {} is OK".format(filename))
			return fparams
		else:
			logging.debug("    > STIMULUS file {} checksum is different => check configuration".format(filename))

		if not 'stimtype' in stimparam:
			logging.error("Couldn't find stimulus type in configuration".format(stimparam))
			return None

		if   stimparam['stimtype'] == 'click':		params=self.get_click_params(stimparam )
		elif stimparam['stimtype'] == 'wave':		params=self.get_wave_params(stimparam )
		elif stimparam['stimtype'] == 'tone':		params=self.get_tone_params(stimparam )
		elif stimparam['stimtype'] == 'SAM-noise':	params=self.get_SAM_params(stimparam )

		if fparams == params:
			logging.debug("    > Stimulus file {} is OK".format(filename))
			return params
		return self.generate(filename,anconfig, stimparam, sectionchecksums)

	def generate(self,filename,anconfig, stimparam, sectionchecksums):
		if self.imported:
			import ZilanyCarney2009AN as an
			import audiotools as at
			self.imported = False
			logging.debug("    > Imported modules for AN")
			logging.debug("    > sys.path = {}".format(sys.path))
		if not 'stimtype' in stimparam:
			logging.error("Couldn't find stimulus type in configuration".format(stimparam))
			return None

		if stimparam['stimtype'] == 'click':     return self.gen_click(  filename, anconfig, stimparam, sectionchecksums)
		if stimparam['stimtype'] == 'wave':      return self.gen_wave(   filename, anconfig, stimparam, sectionchecksums)
		if stimparam['stimtype'] == 'tone':      return self.gen_tone(   filename, anconfig, stimparam, sectionchecksums)
		if stimparam['stimtype'] == 'SAM-noise': return self.gen_SAM(    filename, anconfig, stimparam, sectionchecksums)

	#######################################################################
	#                                                                     #
	#                            CLICK GENERATOR                          #
	#                                                                     #
	#######################################################################
	def get_click_params(self, stimparam):
		params = {
			'stimtype'						: 'click',
			'interaural time difference'	: 0.,
			'interaural level difference'	: 0,
			'stimulus amplitude'			: 80.,
			'stimulus duration'				: 22e-6,
			'delay'							: 0.01,
			'tail'							: 0.1,
			'squeezed'						: True,
			'comment'						: "",
		}

		for par in stimparam:
			params[par] = stimparam[par]
		return params
	def gen_click(self,filename, anconfig, stimparam, sectionchecksums):
		def click(stimdb=40, delay=0.01e-3, clickdur=0.1e-3, stimdur=0.1, smpfreq=100e3):
			"""
			click generates click stimulus.
			"""
			normcoeff = 20e-6*10.0**(float(stimdb)/20.)
			result = np.zeros(int(stimdur*100e3))
			result[int(delay*smpfreq):int((delay+clickdur)*smpfreq)] = 1.
			result *= normcoeff
			return result

		params = self.get_click_params(stimparam)
		params["auditory nerve configuration"] = anconfig
		params["totaldur"] = params["stimulus duration"]+params["delay"]+params["tail"]

		logging.debug("CLICK GENERATOR:")
		for parname in params:
			logging.debug(" > % 31s :{}".format(params[parname])%parname)
		logging.debug(" > % 31s :{}".format(filename)%('output file'))
		logging.debug(" > > > > > > > > > > > > ")

		lftclk = click(
			stimdb	= params["stimulus amplitude"]-params["interaural level difference"],
			delay	= params["delay"]-params["interaural time difference"],
			clickdur= params["stimulus duration"],
			stimdur	= params["totaldur"]
			)
		rttclk = click(
			stimdb	= params["stimulus amplitude"]+params["interaural level difference"],
			delay	= params["delay"]+params["interaural time difference"],
			clickdur= params["stimulus duration"],
			stimdur	= params["totaldur"]
			)
		
		lihc,lsyn,lspk = self.AuditoryNerve(lftclk,anconfig[0])
		rihc,rsyn,rspk = self.AuditoryNerve(rttclk,anconfig[1])
		try:
			with open(filename,"wb") as fd:
				pickle.dump(sectionchecksums,fd)
				pickle.dump(params,fd)
				pickle.dump(lspk,fd)
				pickle.dump(rspk,fd)
				pickle.dump(lftclk,fd)
				pickle.dump(rttclk,fd)
				if not params["squeezed"]:
					pickle.dump(lsyn,fd)
					pickle.dump(rsyn,fd)
					pickle.dump(lihc,fd)
					pickle.dump(rihc,fd)
			return params
		except BaseException as e:
			logging.error(" > Couldn't save file %s: {}".format(e)%filename)
			return None

	#######################################################################
	#                                                                     #
	#                       GENERATOR from WAVE 24                        #
	#                                                                     #
	#######################################################################
	def get_wave_params(sef, stimparam):
		params ={
			'stimtype'					: 'wave',
			'stimulus max. amplitude'	: 75.,
			'resample method'			: 'MEAN',
			'delay'						: 0.01,
			'tail'						: 0.1,
			'squeezed'					: True,
			'comment'					: "",
		}
		for par in stimparam:
			params[par] = stimparam[par]
		return params
	def gen_wave(self,filename, anconfig, stimparam, sectionchecksums):	
		def readWav(wavefile, samplerate=100e3, maxSPL=1200, resample='MEAN',delay=0.01, tail=0.1):
			"""
			read24Wav reads 24 bit wave file and return normolized data for AN model
			Parameters:
				wavefile
				samplerate	- destination sample rate 
				maxSPL		- SPL in dB corresponds to maximal amplitude in wav file (i.e.0x7FFFFF)
							  if maxSPL == None, it returns unscaled data
							  default maxSPL=1200dB
				resample	- method of resample data to samplerate frequency.
							  if 'GNU', it uses GNU libresample (Kazer filters)
							  if 'SCIPY', it uses scipy.signal.resample (fft mapping)
							  if 'MEAN', it calculates mean from both libraries. (default, most accurate method)
							  if 'None', it returns actual data without resampling and scaling
							  default 'MEAN'
				delay		- delay in second before sound. Delay is filled by first sample from sound file.
							  default 0.01
				tail		- duration of silent after stimulus in seconds. Tail filled by last sample from sound file.
			Returns:
				(
					number of channels,
					signal duration in sec,
					data size
					[
						first channel data,
						second channel data,
						....
					]
				)
			"""
			#Read 24 bit wav file
			size,samfreq,nchannels,data= at.readwave(wavefile)
			#Separate channels and add 125 ms of silent at the beginning and at the end
			delaysamples	= int( np.round(samfreq*delay) )
			tailsamples		= int( np.round(samfreq*tail) )
			channels 		= [ np.append(np.linspace(0,data[x],delaysamples),np.append(data[x::nchannels],np.repeat(data[x-nchannels-1],tailsamples))) for x in xrange(nchannels) ]
			signalduration	= float(size+delaysamples+tailsamples)/samfreq #in sec
			hsize			= signalduration *  samplerate
			if resample == "None" or resample == None:
				return nchannels,signalduration,size+samfreq/4,channels
			if resample == "GNU":
				# resampling by GNU libresample (Kazer filters):
				hchannels = [ h[0:hsize] for h in [ at.resample(x, float(hsize)/float(x.size),0) for x in channels] ]
			elif resample == "SCIPY":
				# resampling by scipy.signal (fft mapping):
				hchannels = [ ss.resample(x, hsize) for x in channels]
			elif resample == "MEAN" :
				# Mean value of resample functions by GNU libresample(Kazer filters) and scipy.signal (fft mapping)
				hchannels = map(lambda h,s:(h[1:hsize+1]+s)/2.,[ at.resample(x, float(hsize)/float(x.size),1) for x in channels],[ ss.resample(x, hsize) for x in channels])
			else:
				sys.stderr.write("Cannot recognize resample method. Should be GNU or SCIPY or MEAN\n\n")
				sys.exit(1) 
			if maxSPL != None:
				#Normalization under assumption that maximal signal amplitude in 24bit wave file (i.e.0x7FFFFF) equals to maxSPL dB
				wavcoeff = np.sqrt(2)*20e-6*np.power(10.0,float(maxSPL)/20.)
				hchannels = [ d * wavcoeff for d in hchannels ]
			return nchannels,signalduration,hsize,hchannels

		params = self.get_wave_params(stimparam)
		if not 'input' in params:
			logging.error(" > Couldn't find input file name. ")
			return None
		if not os.access(params['input'],os.R_OK):
			logging.error(" > Couldn't read input file {}.".format(params['input']) )
			return None

		nchannels,sigdur,datasize,data = read24Wav(params["input"],
			maxSPL = parmas["stimulus max. amplitude"],
			resample=parmas["resample method"],
			delay=parmas["delay"], tail=parmas["tail"]
			)
		if nchannels != 2:
			logging.error("Wrong number of channels {} in input file.".format(nchannels,params['input']) )
			return None

		params["number of channels"]=nchannels
		params["auditory nerve configuration"] = anconfig
		params["totaldur"] = sigdur

		logging.debug("WAVE 24 GENERATOR:")
		for parname in params:
			logging.debug(" > % 31s :{}".format(params[parname])%parname)
		logging.debug(" > % 31s :{}".format(filename)%('output file'))
		logging.debug(" > > > > > > > > > > > > ")

		
		lihc,lsyn,lspk = self.AuditoryNerve(data[0],anconfig[0])
		rihc,rsyn,rspk = self.AuditoryNerve(data[1],anconfig[1])
		try:
			with open(filename,"wb") as fd:
				pickle.dump(sectionchecksums,fd)
				pickle.dump(params,fd)
				pickle.dump(lspk,fd)
				pickle.dump(rspk,fd)
				pickle.dump(data[0],fd)
				pickle.dump(data[1],fd)
				if not params["squeezed"]:
					pickle.dump(lsyn,fd)
					pickle.dump(rsyn,fd)
					pickle.dump(lihc,fd)
					pickle.dump(rihc,fd)
			return params
		except BaseException as e:
			logging.error(" > Couldn't save file %s: {}".format(e)%filename)
			return None

	#######################################################################
	#                                                                     #
	#                             TONE GENERATOR                          #
	#                                                                     #
	#######################################################################
	def get_tone_params(self,stimparam):
		params ={
			'stimtype'						: 'tone',			
			'interaural time difference'	: 0.,
			'interaural level difference'	: 0.,
			'stimulus amplitude'			: 80.,
			'stimulus duration'				: 0.1,
			'stimulus frequency'			: 1000.,
			'ramped up'						: 5e-3,
			'ramped down'					: 5e-3,
			'delay'							: 0.01,
			'tail'							: 0.1,
			'squeezed'						: True,
			'comment'						: "",
		}
		for par in stimparam:
			params[par] = stimparam[par]
		return params
	def gen_tone(self,filename, anconfig, stimparam, sectionchecksums):	
		def rampedsin(frequency = 1e3, duration = 0.1, rampup = 5e-3, rampdown = 5e-3, delay = 1e-2, tail = 1e-1, stimdb = 10, smpfreq=100e3):
			"""
			rampedsin generates ramped sinusoidal stimulus.
			"""
			normcoeff =np.sqrt(2)*20e-6*10.0**(float(np.abs(stimdb))/20.)
			t = np.linspace(0, duration, duration * smpfreq+1)
			ramp = (t/rampup)*(t < rampup)+1.0*(t >= rampup)*(t <= duration-rampdown)+(duration-t)/rampdown*(t > duration-rampdown)
			actualdata = float(np.sign(stimdb))*np.sin(2*np.pi*frequency*t)*ramp*normcoeff
			result = np.zeros(delay*smpfreq+actualdata.size+tail*smpfreq)
			result[delay*smpfreq:delay*smpfreq+actualdata.size] =actualdata
			return result
		params = self.get_tone_params(stimparam)

		params["auditory nerve configuration"] = anconfig
		params["totaldur"] = params["stimulus duration"]+params["delay"]+params["tail"]

		logging.debug("TONE GENERATOR:")
		for parname in params:
			logging.debug(" > % 31s :{}".format(params[parname])%parname)
		logging.debug(" > % 31s :{}".format(filename)%('output file'))
		logging.debug(" > > > > > > > > > > > > ")
		
		lsin = rampedsin(
			frequency	= params["stimulus frequency"],
			duration	= params["stimulus duration"],
			stimdb		= params["stimulus amplitude"]-params["interaural level difference"],
			rampup		= params["ramped up"], rampdown = params["ramped down"],
			delay		= params["delay"]-params["interaural time difference"], 
			tail		= params["tail"]+params["interaural time difference"]
		)
		rsin = rampedsin(
			frequency	= params["stimulus frequency"],
			duration	= params["stimulus duration"],
			stimdb		= params["stimulus amplitude"]+params["interaural level difference"],
			rampup		= params["ramped up"], rampdown = params["ramped down"],
			delay		= params["delay"]+params["interaural time difference"], 
			tail		= params["tail"]-params["interaural time difference"]
		)
		lihc,lsyn,lspk = self.AuditoryNerve(lsin,anconfig[0])
		rihc,rsyn,rspk = self.AuditoryNerve(rsin,anconfig[1])

		try:
			with open(filename,"wb") as fd:
				pickle.dump(sectionchecksums,fd)
				pickle.dump(params,fd)
				pickle.dump(lspk,fd)
				pickle.dump(rspk,fd)
				pickle.dump(lsin,fd)
				pickle.dump(rsin,fd)
				if not params["squeezed"]:
					pickle.dump(lsyn,fd)
					pickle.dump(rsyn,fd)
					pickle.dump(lihc,fd)
					pickle.dump(rihc,fd)
			return params
		except BaseException as e:
			logging.error(" > Couldn't save file %s: {}".format(e)%filename)
			return None


	#######################################################################
	#                                                                     #
	#                SINUSOIDAL MODULATED NOISE GENERATOR                 #
	#                                                                     #
	#######################################################################
	def get_SAM_params(self,stimparam):
		params ={
			'stimtype'						: 'SAM-noise',
			'interaural time difference'	: 0.,
			'interaural level difference'	: 0.,
			'modulation deep'				: 0.75,
			'stimulus duration'			    : 0.1,
			'modulation frequency'			: 1000.,
			'stimulus amplitude'			: 80.,
			'modulation ramped up'			: 5e-3,
			'modulation ramped down'		: 5e-3,
			'delay'							: 0.01,
			'tail'							: 0.1,
			'squeezed'						: True,
			'comment'						: "",
			
		}
		for par in stimparam:
			params[par] = stimparam[par]
		return params
	def gen_SAM(self,filename, anconfig, stimparam, sectionchecksums):
		def SAMnoise(frequency=500, duration=0.1, rampup=5e-3, rampdown=5e-3, delay=0.01, tail=0.1, stimdb=80, moddip=0.25):
			"""
			SAMnoise generates sinusoidal modulated noise 
			"""
			smpfreq=100e3
			normcoeff =np.sqrt(2)*20e-6*10.0**(float(np.abs(stimdb))/20.)
			t = np.linspace(0, duration, duration * smpfreq+1)
			ramp = (t < rampup)*(t/rampup)+(t >= rampup)*(t <= duration-rampdown)+(t > duration-rampdown)*(duration-t)/rampdown
			modulation = float(np.sign(stimdb))*((1-moddip/2.)-moddip*np.sin(2*np.pi*frequency*t)/2.)*ramp
			noise = np.random.rand(t.size)*2.-1.
			actualdata = noise*modulation*normcoeff
			result = np.zeros(delay*smpfreq+actualdata.size+tail*smpfreq)
			result[delay*smpfreq:delay*smpfreq+actualdata.size] =actualdata
			return result
		params = self.get_SAM_params(stimparam)
		logging.debug("SINUSOIDAL MODULATED NOISE GENERATOR:")
		params["auditory nerve configuration"] = anconfig
		params["totaldur"] = params["stimulus duration"]+params["delay"]+params["tail"]

		logging.debug("TONE GENERATOR:")
		for parname in params:
			logging.debug(" > % 31s :{}".format(params[parname])%parname)
		logging.debug(" > % 31s :{}".format(filename)%('output file'))
		logging.debug(" > > > > > > > > > > > > ")

		lsin = SAMnoise(
			frequency	= params["modulation frequency"],
			duration	= params["modulation duration"],
			stimdb		= params["stimulus amplitude"]-params["interaural level difference"],
			rampup		= params["ramped up"], rampdown = params["ramped down"],
			delay		= params["delay"]-params["interaural time difference"], 
			tail		= params["tail"]+params["interaural time difference"],
			moddip		= params["modulation deep"]
		)
		rsin = SAMnoise(
			frequency	= params["modulation frequency"],
			duration	= params["modulation duration"],
			stimdb		= params["stimulus amplitude"]+params["interaural level difference"],
			rampup		= params["ramped up"], rampdown = params["ramped down"],
			delay		= params["delay"]+params["interaural time difference"], 
			tail		= params["tail"]-params["interaural time difference"],
			moddip		= params["modulation deep"]
		)
		lihc,lsyn,lspk = self.AuditoryNerve(lsin,anconfig[0])
		rihc,rsyn,rspk = self.AuditoryNerve(rsin,anconfig[1])
		try:
			with open(filename,"wb") as fd:
				pickle.dump(sectionchecksums,fd)
				pickle.dump(params,fd)
				pickle.dump(lspk,fd)
				pickle.dump(rspk,fd)
				pickle.dump(lsin,fd)
				pickle.dump(rsin,fd)
				if not params["squeezed"]:
					pickle.dump(lsyn,fd)
					pickle.dump(rsyn,fd)
					pickle.dump(lihc,fd)
					pickle.dump(rihc,fd)
			return params
		except BaseException as e:
			logging.error(" > Couldn't save file %s: {}".format(e)%filename)
			return None

	def AuditoryNerve(self,
		indata,			# sound pressure in dB ONLY one channel!!!! 
		anconfig,		# set of frequency + fib.type
		cohc	= 1.0,	# normal ohc function
        cihc	= 1.0,	# normal ihc function
        implnt	= 0		# "0" for approximate or "1" for actual implementation of the power-law functions in the Synapse
		):
		"""
		Auditory Nerve Model
		Python wrapper for Zilany et al. 2009 model
		Coded by Timur Pinin (timpin@rambler.ru)
		"""
		#sampling frequency (by default see comemnts in original matlab code)
		Fs			= 100e3 
		anihc		= [ None for x in anconfig ]
		ansyns		= [ None for x in anconfig ]
		anspks		= [ None for x in anconfig ]
		for idx,hc in enumerate(anconfig):
			sys.stderr.write("Activate fiber %fHz: "%hc[0])
			ihc = an.ihc(indata,hc[0],1,1./Fs,indata.size/Fs,cohc,cihc)
			anihc[idx] =  ( hc[0], ihc ) 
			sys.stderr.write("=*=")
			syns, spks = [], []
			for ftype in hc[1:]:
				syn,tsptim,tspsize = an.synapse(ihc,hc[0],1,1./Fs,ftype,implnt)
				spk = [ x for x in tsptim[:tspsize] ]
				spk = np.array( spk ) * 1e3 # spk - spike times in ms
				syns.append(syn)
				spks.append(spk)
				sys.stderr.write(".")
			ansyns[idx] = ( hc, syns )
			anspks[idx] = ( hc, spks )
			sys.stderr.write(" done\n")
		return anihc,ansyns,anspks

def genconf(config):
	def regen(config):
		ret = [ [], [] ]
		for n in xrange(config["nhcell"]):
			#DB>>
			#nspace = config
			#<<DB
			fr = config["cell distribution"](n)
			l,r=[fr],[fr]
			for k in xrange(config["nfibperhcell"]):
				l.append( config["fiber distribution"](n,k) )
				r.append( config["fiber distribution"](n,k) )
			ret[0].append(l)
			ret[1].append(r)
		return ret
	def regen_and_save(config):
		anconf = regen(config)
		if not "file" in config: return anconf
		with open(config["file"], "wb") as fd:
			pickle.dump(config['__:hash:__'],fd)
			pickle.dump(anconf,fd)
		logging.debug("    > Successfully regenerate configuration:{}")
		logging.debug("    > New checksum is : {}".format(config['__:hash:__']))
		logging.debug("    > New configuration is : {}".format(anconf))
		logging.info("    > DONE")
		return anconf
	logging.info(" > CHECK AUDITORY NERVE configuration")
	if not "file" in config: return regen(config)
	if not os.access(config["file"],os.R_OK):return regen_and_save(config)
	with open(config["file"], "rb") as fd:
		try:
			cfghash = pickle.load(fd)
			anconf  = pickle.load(fd)
		except BaseException as e:
			logging.error(" > Cannot load AUDITORY NERVE configuration file {}.".format(config["file"]))
			return regen_and_save(config)
			
	if cfghash != config['__:hash:__']:
		logging.debug("    > Checksum of AN configurations are not equal: regenerate configuration")
		return regen_and_save(config)
	else:
		logging.debug("    > Checksums are the same {}".format(cfghash))
		logging.debug("    > Successfully read an configuration:{}".format(anconf))
		logging.info("    > DONE")
		return anconf
		

if __name__ == "__main__":
	def printHUM(hlp):
		def printHUMitem(item,params):
			print "========================STIMULUS=:=%s================="%(item)
			print "{} : {}".format("% 32s"%'stimtype',params['stimtype'])
			for p in params:
				if p == 'stimtype':continue
				print "{} : {}".format("% 32s"%p,params[p])
			print
		printHUMitem("CLICK",hlp.get_click_params({}) )
		printHUMitem("WAVE", hlp.get_wave_params({})  )
		printHUMitem("TONE", hlp.get_tone_params({})  )
		printHUMitem("SAM",  hlp.get_SAM_params({})   )
	def printTBL(hlp):
		def printTBLitem(item,params):
			print "||{}||{}||{}||".format(item,'stimtype',params['stimtype'])
			for p in params:
				if p == 'stimtype':continue
				print "|| ||{}||{}||".format(p,params[p])
		print "||STIMULUS||PARAMETER||DEFAULT VALUE||"
		printTBLitem("CLICK",hlp.get_click_params({}) )
		printTBLitem("WAVE", hlp.get_wave_params({})  )
		printTBLitem("TONE", hlp.get_tone_params({})  )
		printTBLitem("SAM",  hlp.get_SAM_params({})   )
		
	def printXML(hlp):
		def printXMLnode(node,params):
			print "\t<{} stimtype=\"{}\">".format(node,params['stimtype'])
			for p in params:
				if p == 'stimtype':continue
				print "\t\t<{}>{}</{}>".format(p,params[p],p)
			print "\t</%s>"%node
		print "<STIMULI>"
		printXMLnode("CLICK",hlp.get_click_params({}) )
		printXMLnode("WAVE", hlp.get_wave_params({})  )
		printXMLnode("TONE", hlp.get_tone_params({})  )
		printXMLnode("SAM",  hlp.get_SAM_params({})   )
		print "</STIMULI>"
	hlp = angen()
	if len(sys.argv) < 2:
		print "USAGE: %s [HUM|TBL|XML]"%sys.argv[0]
		sys.exit(0)
	for i in sys.argv[1:]:
		if i == "-h" or i == "--help":
			print "USAGE: %s [HUM|TBL|XML]"%sys.argv[0]
			sys.exit(0)
		if i == "HUM":printHUM(hlp)
		if i == "TBL":printTBL(hlp)
		if i == "XML":printXML(hlp)
	
