import os,sys,ConfigParser, types, hashlib
import logging
from ConfigParser import ConfigParser
import numpy as np
import scipy as sp

from tools.commonvariables import config

def nameresolv(item,nspace,currentsection):
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
			if var[0] != currentsection:
				if not '__:dependency:__' in nspace[currentsection]:
					nspace[currentsection]['__:dependency:__'] = {}
				nspace[currentsection]['__:dependency:__'][var[0]] = True
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
		if var[0] != currentsection:
			if not '__:dependency:__' in nspace[currentsection]:
				nspace[currentsection]['__:dependency:__'] = {}
			nspace[currentsection]['__:dependency:__'][var[0]] = True
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
	except BaseException as e:
		logging.warning("couldn't read file %s. Error:%s"%(filename,e) ) 
		return nspace
	if sections == None:
		sections = config.sections()
	for section in sections:
		if skipit(section,skip) : continue
		if not section in nspace: nspace[section]={}
		if not config.has_section(section): continue
		if not '__:hash:__' in nspace[section]:			nspace[section]['__:hash:__']=hashlib.sha256()
		if not '__:dependency:__' in nspace[section]:	nspace[section]['__:dependency:__']={}
		for option in config.options(section):
			if option in nspace[section]:
				logging.error("Name conflict option \'%s\' exists in section [\'%s\']"%(option,section) ) 
				return {}				
			xitem = unicode( config.get(section,option) )
			item = nameresolv(xitem,nspace,section)
			if item == None:
				logging.error("Problem with resolving option in  [\'%s\']\'%s\'=\'%s\'"%(section,option,item) ) 
				return {}
			try:
				exec "nspace[\""+section+"\"][\""+option+"\"]="+item
				nspace[section]['__:hash:__'].update(xitem)
			except BaseException as e:
				logging.warning("Problem with reading configuration from the %s"%filename) 
				logging.warning("Cannot read section: \'%s\', option: \'%s\'"%(section,option) )
				logging.warning("        %s"%item)
				logging.warning("Exception: %s"%e)
				logging.warning("!!!! SKIPPED IT !!!!")
				pass
	# Calculate hash
	for section in sections:
		if skipit(section,skip) : continue
		if not '__:hash:__' in nspace[section]:
			logging.warning("Cannot find hash object to calculate hashsum of section %s"%section)
			continue
		nspace[section]['__:hash:__'] = nspace[section]['__:hash:__'].hexdigest()
	
	for section in sections:
		if skipit(section,skip) : continue
		if not '__:dependency:__' in nspace[section]:continue
		for parents in nspace[section]['__:dependency:__']:
			if not '__:hash:__' in nspace[parents]:
				logging.warning("Cannot find hash sum in parent section \'%s\' to add to dependent section \'%s\'"%(parent,section))
				continue
			nspace[section]['__:hash:__'] += nspace[parents]['__:hash:__']
		logging.debug(" > Section % 14s is successfully processed"%(section))
		logging.debug(" >      Section hash-sum : {}".format(nspace[section]['__:hash:__']))
		logging.debug(" >    Section dependency : {}".format([ str(parents) for parents in nspace[section]['__:dependency:__'] ]))
		del nspace[section]['__:dependency:__']
	return nspace

if __name__ == "__main__":
	cfg = cofread(sys.argv[1])
	print cfg
	for s in cfg:
		print "Section:",s
		for o in cfg[s]:
			print "     Option ",o,type(cfg[s][o])," =", cfg[s][o]
			
