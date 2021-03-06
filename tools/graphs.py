import os,sys,csv
import numpy as np
try:
    import cPickle as pickle
except:
    import pickle
import logging,time
import matplotlib.pyplot as plt
from tools.commonvariables import *

def check_stimname(stimname):
	if not stimname in stimlist:
		raise ValueError("Couldn't find stimulus name \'%s\' in stimlist"%(stimname))
		
def plot_traces(stimname,recname,mrange=None):
	check_stimname(stimname)
	if type(recname) is tuple or type(recname) is list:
		for rname in recname:
			plot_traces(stimname,rname,mrange)
		return
	if not recname in stimlist[stimname][1]:
		raise ValueError("Couldn't find record name \'%s\' in stimlist"%(recname))
	reclist = list( stimlist[stimname][1][recname] )
	if mrange != None:
		if type(mrange) is int and len(reclist) > mrange:
			reclist = [ reclist[mrange] ]
		elif type(mrange) is float and 0. < mrange < 1.0:
			reclist = reclist[::int((len(reclist)-1)*mrange)]
		elif type(mrange) is tuple:
			mrange = list(mrange)
			if mrange[0] == None: mrange[0] = 0
			if mrange[1] == None: mrange[1] = len(reclist)
			if len(mrange) == 2:
				reclist = reclist[mrange[0]:mrange[1]]
			if len(mrange) == 3:
				reclist = reclist[mrange[0]:mrange[1]:mrange[2]]
		elif type(mrange) is list:
			nreclist = []
			for recid in mrange:
				if recid < len(reclist):
					nreclist.append(reclist[recid])
			reclist = nreclist

	tvec = stimlist[stimname][2]
	stimlist[stimname][4][tvec[0]].seek(tvec[1])
	tvec = pickle.load(stimlist[stimname][4][tvec[0]])
	tvec = tvec[1]
	for xrec in reclist:
		xvec = xrec[1]
		stimlist[stimname][4][xvec[0]].seek(xvec[1])
		xvec = pickle.load(stimlist[stimname][4][xvec[0]])
		xvec = xvec[4]
		plt.plot(tvec,xvec)

def getpoplist(stimname,popname,mrange=None):
	if not popname in stimlist[stimname][0]:
		raise ValueError("Couldn't find population name \'%s\' in stimlist"%(popname))
	poplist = list( stimlist[stimname][0][popname] )
	if mrange != None:
		if type(mrange) is int and len(poplist) > mrange:
			poplist = [ poplist[mrange] ]
		elif type(mrange) is float and 0. < mrange < 1.0:
			poplist = poplist[::int((len(poplist)-1)*mrange)]
		elif type(mrange) is tuple:
			mrange = list(mrange)
			if mrange[0] == None: mrange[0] = 0
			if mrange[1] == None: mrange[1] = len(poplist)
			if len(mrange) == 2:
				poplist = poplist[mrange[0]:mrange[1]]
			if len(mrange) == 3:
				poplist = poplist[mrange[0]:mrange[1]:mrange[2]]
		elif type(mrange) is list:
			npoplist = []
			for popid in mrange:
				if popid < len(poplist):
					npoplist.append(poplist[popid])
			poplist = npoplist
	return poplist

def plot_raster(stimname,popname,mrange=None):
	check_stimname(stimname)
	if type(popname) is tuple or type(popname) is list:
		for pname in popname:
			plot_raster(stimname,pname,mrange)
		return
	for xpop in getpoplist(stimname,popname,mrange):
		xvec = xpop[1]
		stimlist[stimname][4][xvec[0]].seek(xvec[1])
		xspk = pickle.load(stimlist[stimname][4][xvec[0]])
		xgid = xspk[1]
		xspk = xspk[2]
		plt.plot(xspk,np.repeat(xgid, xspk.size),"k|")

def plot_stimwave(stimname,isright=False):
	if not "STIMULI" in config:
		raise ValueError("Couldn't find STIMULI SECTION in config")
	if not stimname in config["STIMULI"]:
		raise ValueError("Couldn't find stimulus name \'%s\' in STIMULI section"%(stimname))
	stimfile = config["STIMULI"][stimname][0]
	if not type(isright) is bool:
		if type(isright) is int or type(isright) is float:
			isright = bool(isright)
		elif  type(isright) is str:
			isright = isright.upper()
			isright = isright == "YES" or isright == "Y" or\
			          isright == "RIGHT" or isright == "R"
		else:
			ValueError("isright parameter has a wrong value")
	with open(stimfile,"rb") as fd:
		checksum = pickle.load(fd)
		param = pickle.load(fd)
		xxx = pickle.load(fd); del xxx
		xxx = pickle.load(fd); del xxx
		wave = pickle.load(fd)
		if isright:
			wave = pickle.load(fd)
	stimdur = int(wave.size)
	plt.plot(np.arange(stimdur)/100.,wave,"k-")
	
def calculate_spikerate(stimname,population,nbins=100,binsize=1.,mrange=None, tstim=None):
	check_stimname(stimname)
	sprate = np.zeros(nbins, dtype=np.dtype('i'))
	poplist = getpoplist(stimname,population,mrange)
	for xpop in poplist:
		xvec = xpop[1]
		stimlist[stimname][4][xvec[0]].seek(xvec[1])
		xspk = pickle.load(stimlist[stimname][4][xvec[0]])[2]
		if tstim != None and (type(tstim) is float or type(tstim) is int):
			xspk = xspk[ np.where( xspk >= float(tstim) ) ]
			xspk -= float(tstim)
		xspk = xspk[ np.where( xspk < float(nbins*binsize) ) ]
		if len(xspk) <= 0: continue
		xspk = np.floor(xspk/binsize).astype(int)
		sprate[ xspk ] += 1
	return sprate,len(poplist)

def plot_population_spikerate(stimname,popname,nbins=100,binsize=1.,mrange=None,normalaize=False,tstim=None,color="k",alpha=1.0):
	if type(popname) is tuple or type(popname) is list:
		sprate = np.zeros(nbins, dtype=np.dtype('i'))
		xcount = 0
		for pname in popname:
			nspr, nsize = calculate_spikerate(stimname,pname,nbins,binsize,mrange,tstim)
			sprate += nspr
			xcount += nsize
	else:
		sprate, xcount = calculate_spikerate(stimname,popname,nbins,binsize,mrange,tstim)
	if normalaize:
		sprate /= xcount
	plt.bar(np.arange(nbins)*binsize-0.45*binsize,sprate,0.9*binsize,color=color,edgecolor=color,alpha=alpha)

def plot_stimrate(popname,mrange=None,stimuli=None,m0a0t='ave',tstim=None,nbins=100,binsize=1.,separate=False,color=None):
	if stimuli == None :
		stimuli = stimnames
	x = np.arange(len(stimuli))
	if separate and ( type(popname) is tuple or type(popname) is list ):
		y = np.zeros( (len(stimuli), len(popname)) )
	else:
		y = np.zeros(len(stimuli))
	if tstim != None and type(tstim) is tuple and len(tstim) != len(stimuli):
		ValueError("tstim in tuple sets simulus moment for each simulation. It should have same size as number of stimuli")
	if nbins != None and type(nbins) is tuple and len(nbins) != len(stimuli):
		ValueError("nbins in tuple sets simulus moment for each simulation. It should have same size as number of stimuli")
	if binsize != None and type(binsize) is tuple and len(binsize) != len(stimuli):
		ValueError("binsize in tuple sets simulus moment for each simulation. It should have same size as number of stimuli")

	if type(popname) is tuple or type(popname) is list:
		if separate:
			for idx, stimname in enumerate(stimuli):
				tsm = tstim[idx]   if tstim != None   and type(tstim)   is tuple else tstim
				nbs = nbins[idx]   if nbins != None   and type(nbins)   is tuple else nbins
				bsz = binsize[idx] if binsize != None and type(binsize) is tuple else binsize
		
				shift = 0.8/float( len( popname ) )
				for pid,pname in enumerate( popname ):
					sprate, xcount = calculate_spikerate(stimname,pname,mrange=mrange,tstim=tsm,binsize=bsz,nbins=nbs)
					if m0a0t == 'max' or m0a0t == 'M': y[idx][pid] = np.max(sprate)
					if m0a0t == 'ave' or m0a0t == 'a': y[idx][pid] = np.mean(sprate)
					if m0a0t == 'tot' or m0a0t == 'T': y[idx][pid] = np.sum(sprate)
			for pid,pname in enumerate( popname ):
				if color == None:
					plt.bar(x+shift*pid-0.4,y[:,pid],shift,color="k",label=pname)
				else:
					plt.bar(x+shift*pid-0.4,y[:,pid],shift,color=color[pid],label=pname)
		else:
			for idx, stimname in enumerate(stimuli):
				tsm = tstim[idx]   if tstim != None   and type(tstim)   is tuple else tstim
				nbs = nbins[idx]   if nbins != None   and type(nbins)   is tuple else nbins
				bsz = binsize[idx] if binsize != None and type(binsize) is tuple else binsize
				sprate = np.zeros(nbins, dtype=np.dtype('i'))
				xcount = 0
				for pname in popname:
					nspr, nsize = calculate_spikerate(stimname,pname,mrange=mrange,tstim=tsm,binsize=bsz,nbins=nbs)
					sprate += nspr
					xcount += nsize
				if m0a0t == 'max' or m0a0t == 'M': y[idx] = np.max(sprate)
				if m0a0t == 'ave' or m0a0t == 'a': y[idx] = np.mean(sprate)
				if m0a0t == 'tot' or m0a0t == 'T': y[idx] = np.sum(sprate)
			plt.bar(x-0.4,y,0.8,color="k")
	else:
			for idx, stimname in enumerate(stimuli):
				tsm = tstim[idx]   if tstim != None   and type(tstim)   is tuple else tstim
				nbs = nbins[idx]   if nbins != None   and type(nbins)   is tuple else nbins
				bsz = binsize[idx] if binsize != None and type(binsize) is tuple else binsize
				sprate, xcount = calculate_spikerate(stimname,popname,mrange=mrange,tstim=tsm,binsize=bsz,nbins=nbs)
				if m0a0t == 'max' or m0a0t == 'M': y[idx] = np.max(sprate)
				if m0a0t == 'ave' or m0a0t == 'a': y[idx] = np.mean(sprate)
				if m0a0t == 'tot' or m0a0t == 'T': y[idx] = np.sum(sprate)
			plt.bar(x-0.4,y,0.8,color="k")
	plt.xticks(x, stimuli, rotation='vertical')
	plt.subplots_adjust(bottom=0.15)
