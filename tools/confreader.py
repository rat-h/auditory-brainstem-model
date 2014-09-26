import os,sys,ConfigParser, types
import logging
from ConfigParser import ConfigParser
import numpy as np
import scipy as sp

from tools.commonvariables import config

def nameresolv(item,nspace):
	copir = item.split("$")
	if len(copir) < 2: 
		res = item
	else:
		res = ''
		for pre,var in map(None,copir[::2],copir[1::2]):
			if pre != None: res += pre
			if var == None: continue
			var = var.split(":")
			if len(var) != 2: return None
			if not var[0] in nspace : return None
			if not var[1] in nspace[var[0]] : return None
			if type(nspace[var[0]][var[1]]) is types.LambdaType and nspace[var[0]][var[1]].__name__ == '<lambda>':
				res += 'nspace["%s"]["%s"]'%tuple(var)
				#res += 'config["%s"]["%s"]'%tuple(var)
			else:
				res += str(nspace[var[0]][var[1]])
				#res += 'config["%s"]["%s"]'%tuple(var)
	copir = res.split("@")
	if len(copir) < 2: return res
	res = ''
	for pre,var in map(None,copir[::2],copir[1::2]):
		if pre != None: res += pre
		if var == None: continue
		var = var.split(":")
		if len(var) != 2: return None
		if not var[0] in nspace : return None
		if not var[1] in nspace[var[0]] : return None
		res += 'nspace["%s"]["%s"]'%tuple(var)
	return unicode(res)

def confreader(filename,nspace = {}):
	"""
	Reads file with configurations and returns dictionary with sections
	and options. All options will be turned into python objects (DON'T 
	FORGET PUT ALL STRING OPTIONS WITHIN QUOTES).
	
	You can use @SECTION:OPTION@ notation to refer to existed python object,
	or $SECTION:OPTION$ to convert object back into a string and insert a string.
	
	Returns option dictionary or {}. 
	Empty dictionary indicates error with file opening, reading or parsing.
	
	If confreader couldn't turn option into some python object, this 
	options is skipped and Warning message will put in logger.
		
	"""
	if 	filename == None:
		return nspace
	if not os.access(filename,os.R_OK):
		return nspace
	config = ConfigParser()
	config.optionxform=str
	try:
		config.read( filename )
	except :
		return nspace
	for section in config.sections():
		if not section in nspace: nspace[section]={}
		for option in config.options(section):
			if option in nspace[section]:
				logging.error("Name conflict option \'%s\' exists in section [\'%s\']"%(option,section) ) 
				return {}				
			xitem = unicode( config.get(section,option) )
			item = nameresolv(xitem,nspace)
			if item == None:
				logging.error("Problem with resolving option in  [\'%s\']\'%s\'=\'%s\'"%(section,option,item) ) 
				return {}
			try:
				exec "nspace[\""+section+"\"][\""+option+"\"]="+item
			except :
				logging.warning("Problem with reading configuration from the %s"%filename) 
				logging.warning("Cannot read section: \'%s\', option: \'%s\'"%(section,option) )
				logging.warning("        %s"%item)
				logging.warning("!!!! SKIPPED IT !!!!")
				pass
			
	return nspace

if __name__ == "__main__":
	cfg = cofread(sys.argv[1])
	print cfg
	for s in cfg:
		print "Section:",s
		for o in cfg[s]:
			print "     Option ",o,type(cfg[s][o])," =", cfg[s][o]
			
