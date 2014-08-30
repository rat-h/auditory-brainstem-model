import os,sys,csv
import numpy as np
try:
    import cPickle as pickle
except:
    import pickle
import logging,time
from tools.commonvariables import *

def check_stimname(stimname):
	if not stimname in stimlist:
		raise ValueError("Couldn't find stimulus name \'%s\' in stimlist"%(stimname))

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

def stat_total(stimname,popname,mrange=None,Norm=False,trange=None):
	check_stimname(stimname)
	if type(popname) is tuple or type(popname) is list:
		summ = 0
		for pname in popname:
			summ += stat_total(stimname,pname,mrange,trange)
		if Norm:
			return summ/float(len(popname))
		else:
			return summ
	summ = 0
	for xpop in getpoplist(stimname,popname,mrange):
		xvec = xpop[1]+stimlist[stimname][3]
		stimlist[stimname][4].seek(xvec)
		xspk = pickle.load(stimlist[stimname][4])
		xspk = xspk[2]
		if type(trange) is int or type(trange) is float:
			if trange >= 0:
				xspk = xspk[ np.where( xspk >= float(trange) ) ]
			else:
				xspk = xspk[ np.where( xspk < np.abs(float(trange)) ) ]
		elif type(trange) is list or type(trange) is tuple:
			if len(trange) !=2:
				raise ValueError("trange should be int, float or list/tuple size of 2")
			xspk = xspk[ np.where( xspk >= float(trange[0]) ) ]
			xspk = xspk[ np.where( xspk <= float(trange[1]) ) ]
		summ += len(xspk)
	return summ

def getR2XYN(stimname,popname,frequency,tstim, mrange=None,Norm=False,trange=None):
	X,Y,N = 0.,0.,0
	for xpop in getpoplist(stimname,popname,mrange):
		xvec = xpop[1]+stimlist[stimname][3]
		stimlist[stimname][4].seek(xvec)
		xspk = pickle.load(stimlist[stimname][4])
		xspk = xspk[2]
		if type(trange) is int or type(trange) is float:
			if trange >= 0:
				xspk = xspk[ np.where( xspk >= float(trange) ) ]
			else:
				xspk = xspk[ np.where( xspk < np.abs(float(trange)) ) ]
		if type(trange) is list or type(trange) is tuple:
			if len(trange) !=2:
				raise ValueError("trange should be int, float or list/tuple size of 2")
			xspk = xspk[ np.where( xspk >= float(trange[0]) ) ]
			xspk = xspk[ np.where( xspk <= float(trange[1]) ) ]
		Y += np.sum( np.sin((xspk-tstim)*2.*np.pi*float(frequency)/1000.0) )
		X += np.sum( np.cos((xspk-tstim)*2.*np.pi*float(frequency)/1000.0) )
		N += len(xspk)
	return X,Y,N
	
def stat_R2(stimname,popname,frequency,tstim,mrange=None,Norm=False,trange=None,R2only=True):
	check_stimname(stimname)
	
	if type(popname) is str:
		popname = [ popname ]
	X,Y,N = 0.,0.,0
	for pname in popname:
		x,y,n= getR2XYN(stimname,pname,frequency,tstim,mrange,trange)
		X += x
		Y += y
		N += n
	if N == 0 :
		return 0.0 if R2only else (0.0, 0,0)
	return (X/N)**2 + (Y/N)**2 if R2only else ( (X/N)**2 + (Y/N)**2, np.arctan2(X/N, Y/N) )
