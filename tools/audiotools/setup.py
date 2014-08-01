def configuration(parent_package='', top_path=None):
	import numpy
	from numpy.distutils.misc_util import Configuration

	config = Configuration('audiotools',parent_package,top_path)
	config.add_extension('audiotools', ['audiotools.c'],
		extra_link_args=[os.getcwd()+'/libresample-0.1.3/libresample.a'], 
		depends=['libresample-0.1.3/libresample.a'],
		include_dirs=['libresample-0.1.3/include/'])
	return config

if __name__ == "__main__":
	import os
	os.system('pushd libresample-0.1.3 && ./configure CFLAGS=-fPIC && make &&popd')
	from numpy.distutils.core import setup
	setup(
		name = "audiotools",
		version='0.01',
		description='Python wrapper for GNU libresample-0.1.3 and reader Wave 24 files',
		author='Ruben Tikidji-Hamburyan, Timur Pinin',
		author_email='rth@nisms.krinc.ru, timpin@rambler.ru',
		configuration=configuration
	)


#audiotools.c 
