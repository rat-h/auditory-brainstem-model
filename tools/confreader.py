import os,sys,ConfigParser, types, hashlib
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

def skipit(section,skip):
	if skip == None: return False
	if type(skip) is str:
		if section == skip: return True
	if type(skip) is list or type(skip) is tuple:
		if section in skip:  return True
	return False
def confreader(filename,nspace = {},sections=None,skip=None):
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
		logging.warning("couldn't find file: %s"%(filename) ) 
		return nspace
	config = ConfigParser()
	config.optionxform=str
	try:
		config.read( filename )
	except :
		logging.warning("couldn't read file: %s"%(filename) ) 
		return nspace
	if sections == None:
		sections = config.sections()
	for section in sections:
		if skipit(section,skip) : continue
		if not section in nspace: nspace[section]={}
		if not config.has_section(section): continue
		if not '__:hash:__' in nspace[section]:nspace[section]['__:hash:__']=hashlib.sha256()
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
				nspace[section]['__:hash:__'].update(xitem)
			except :
				logging.warning("Problem with reading configuration from the %s"%filename) 
				logging.warning("Cannot read section: \'%s\', option: \'%s\'"%(section,option) )
				logging.warning("        %s"%item)
				logging.warning("!!!! SKIPPED IT !!!!")
				pass
	# Calculate hash
	for section in sections:
		if skipit(section,skip) : continue
		if not '__:hash:__' in nspace[section]:continue
		nspace[section]['__:hash:__'] = nspace[section]['__:hash:__'].hexdigest()
	
	return nspace

if __name__ == "__main__":
	cfg = cofread(sys.argv[1])
	print cfg
	for s in cfg:
		print "Section:",s
		for o in cfg[s]:
			print "     Option ",o,type(cfg[s][o])," =", cfg[s][o]
			
