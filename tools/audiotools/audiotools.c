#include <Python.h>
#include <numpy/arrayobject.h>
#include <unistd.h>
#include <fcntl.h>
#include "libresample.h"

static PyObject *readwave(PyObject *self, PyObject *args);
static PyObject *resample(PyObject *self, PyObject *args);


static PyMethodDef audiotoolsmethods[] = {
	{"readwave", readwave,METH_VARARGS},
	{"resample", resample, METH_VARARGS},
	{NULL, NULL}
};

void initaudiotools() {
	(void) Py_InitModule("audiotools",audiotoolsmethods);
	import_array();
}
typedef struct{
	unsigned int RIFF;
	int Long;
	unsigned int WAVE;
	unsigned int FMT;
	int ChunkSize;
	short FormatTag, Channels;
	int Frequency, BytePerSecond;
	short SamplSize, BitSamplSize;
	unsigned int DATA;
	int DataLong;
} wav_h;


PyObject *readwave(PyObject *self, PyObject *args){

	char *filename;
	wav_h header;
	int mfd = -1;
	PyArrayObject *Vecout;
	
	if( !PyArg_ParseTuple(args,"s",
	&filename) ) return NULL;
	if( ( mfd  = open(filename,O_RDONLY,0) ) < 0 ){
		PyErr_Format(PyExc_ValueError,"Couldn\'t read file: %s\n",filename);
		return NULL;
	}

	if( read(mfd, &header,44) != 44){
		PyErr_Format(PyExc_ValueError,"Couldn\'t read header of %s \n",filename);
		return NULL;
	}
	if( header.RIFF != 1179011410 ||
		header.WAVE != 1163280727 ||
		header.FMT  != 544501094  ||
		header.DATA != 1635017060 
	){
		PyErr_Format(PyExc_ValueError,"Identification field\n");
		return NULL;
	}
/*
	if( header.ChunkSize != 16 || header.BitSamplSize != 24 ||
		header.SamplSize != header.Channels * 3 ||
		header.FormatTag != 1 ){
		PyErr_Format(PyExc_ValueError,"File isn\'t 24bit wave format. Please use another library\n");
		return NULL;
	}
*/
	int dims = header.Channels * header.DataLong/header.SamplSize;
	
	Vecout = (PyArrayObject *) PyArray_FromDims( 1, &dims, NPY_DOUBLE);
	if(Vecout == NULL){
		PyErr_Format(PyExc_ValueError,"Cannot Allocated Memory for data\n");
		return NULL;
	}
	
	double *out = (double*)Vecout->data;
	//DB>>
	//fprintf(stderr,"\n*** NChannel = %d ***\n",header.Channels);
	//printf("%d\n",header.SamplSize);
	//<<DV
	int bithread, stchunk=header.SamplSize*256, samhread, cnt;
	unsigned char buffer[stchunk+1], *scan24;
	memset(buffer,0,stchunk);
	int scan64;
	int stp = header.SamplSize / header.Channels;
	//DB>>
	//int gcnt=0;
	//<<DB
	
	while( (bithread = read(mfd,&buffer,stchunk)) != 0){
		samhread = bithread / stp;
		//DB>>
		//fprintf(stderr,"Read: byte=%d, samples = %d\n", bithread,samhread );
		//<<DB
		for(scan24 = buffer,cnt=0, scan64=*((int*)scan24);
			cnt < samhread; scan24 += stp, ++cnt, scan64=*((int*)scan24) ) {
			*(out++) = (header.BitSamplSize == 24) ? 
				(double)((int)((scan64 << 8)&0xFFFFFF00))/(double)0x7FFFFF00 :
				(double)((int)((scan64 << 16)&0xFFFF0000))/(double)0x7FFF0000;
			//DB>>
			//gcnt++;
			//fprintf(stderr,"\tcnt = %d of %d\n",cnt, samhread);
			//fprintf(stderr,"\t%02X:%02X:%02X => %08X => %08X => %d => %g\n", scan24[2],scan24[1],scan24[0], scan64,(scan64 << 8)&0xFFFFFF00 ,(scan64 << 8)&0xFFFFFF00,(double)(int)((scan64 << 8)&0xFFFFFF00));
			//<<DB
		}
	}
	//DB>>
	//printf("*** GCNT:%d ***\n",gcnt);
	//<<DB
	close(mfd);

	PyObject *result = PyTuple_New(4);
	if ( PyTuple_SetItem(result,0,PyInt_FromLong(header.DataLong/header.SamplSize)) ) return NULL;
	if ( PyTuple_SetItem(result,1,PyInt_FromLong(header.Frequency)) ) return NULL;
	if ( PyTuple_SetItem(result,2,PyInt_FromLong(header.Channels)) ) return NULL;
	if ( PyTuple_SetItem(result,3,(PyObject*)Vecout) ) return NULL;
	return result;
}

static PyObject *resample(PyObject *self, PyObject *args){
	PyArrayObject *Vecin, *Vecout;
	double *vecin, *vecout;
	double factor = -1.;
	int vecinsize, vecoutsize, accuracy;
	
	if( !PyArg_ParseTuple(args,"O!di", &PyArray_Type, &Vecin, &factor,&accuracy)
	  ||  Vecin == NULL ) return NULL;
	if( Vecin->descr->type_num != NPY_DOUBLE  || Vecin->nd != 1){
		PyErr_SetString( PyExc_ValueError ,"It isn\'t one dimensional array of FOLAT type." );
		return NULL;
	}
	if( (vecinsize = Vecin->dimensions[0]) < 3){
		PyErr_Format( PyExc_ValueError ,"input vector too small ( size = %d )\n",vecinsize);
		return NULL;
	}
	if( factor <= 0.0){
		PyErr_Format( PyExc_ValueError ,"factor should be positive number ( %g )\n",factor);
		return NULL;
	}
	vecin = (double*)Vecin->data;
	vecoutsize = (int)ceil((double)vecinsize*factor)+1;
	Vecout	= (PyArrayObject*) PyArray_FromDims(1,&vecoutsize,NPY_DOUBLE);
	vecout  = (double*)Vecout->data;
	void *handler = resample_open(accuracy,factor,factor);
	int fwidth = resample_get_filter_width(handler), bufferused, result;
	if( (result = resample_process(handler, factor, vecin, vecinsize, 1, &bufferused, vecout, vecoutsize) ) < 0){
		PyErr_Format( PyExc_ValueError ,"resample_process return an error ( %d )\n",result);
		return NULL;
	}
	resample_close(handler);
	return PyArray_Return(Vecout);
}

