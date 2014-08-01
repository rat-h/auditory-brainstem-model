def configuration(parent_package='', top_path=None):
	import numpy
	from numpy.distutils.misc_util import Configuration

	config = Configuration('ZilanyCarney2009AN',parent_package,top_path)
	config.add_extension('ZilanyCarney2009AN', ['catmodel_IHC.c','catmodel_Synapse.c', 'complex.c', 'ZilanyCarney2009AN.c'])
	#config.add_subpackage('ffGn.py')
	config.add_data_files((None,'ffGn.py'))
	return config

if __name__ == "__main__":
	from numpy.distutils.core import setup
	setup(
		name = "ZilanyCarney2009AN",
		version='0.01',
		description='Python wrapper for Zilany, et al 2009 auditory nerve model',
		author='Ruben Tikidji-Hamburyan, Timur Pinin',
		author_email='rth@nisms.krinc.ru, timpin@rambler.ru',
		configuration=configuration
	)


