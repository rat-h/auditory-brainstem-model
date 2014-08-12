#! /bin/bash
#set -x

case $1 in
	clean)
		pushd tools
		rm -fR ZilanyCarney2009AN.so ffGn.py audiotools.so ZilanyCarney-JASAcod-2009/build audiotools/build lib* *.pyc
		pushd audiotools/libresample-0.1.3; [ -e Makefile ] && make dist; popd
		popd
		pushd ../tools
		rm -fR ZilanyCarney2009AN.so ffGn.py audiotools.so
		popd
		rm -fR *.mod network.pkl i686 x86_64 log/*.log *.log
#Results/*
		;;
	make)
		LOCALLIB="lib."$(uname -s | tr '[:upper:]' '[:lower:]')"-"$(uname -m)"-"$(python -V 2>&1 | sed "s|.* ||g" | cut -f "1 2" -d ".")
		pushd tools &&
			pushd ZilanyCarney-JASAcod-2009 && python setup.py install --prefix=../ && popd && 
			pushd audiotools && 
				pushd libresample-0.1.3 && 
					( [ -e Makefile ] && make dist );  ./configure && make && sleep 1 &&
				popd &&
				python setup.py install --prefix=../ && 
			popd && 
			for i in $(find lib* -name "*.so"); do ln -s $i; done
			for i in $(find lib* -name "*.py"); do ln -s $i; done
		popd
		;;
	*)
		$0 clean 
		$0 make
		;;
esac

echo "DONE"

