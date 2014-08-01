#include <Python.h>
#include <numpy/arrayobject.h>

//declaration of core function. It should be static to prevent overlapping 
int IHCAN(double *, double, int, double, int, double, double, double *);
int SingleAN(double *px, double cf, int nrep, double tdres, int totalstim, double fibertype, int implnt, double *synout, double *psth);
static PyObject *ihc(PyObject *self, PyObject *args);
static PyObject *synapse(PyObject *self, PyObject *args);
static PyObject *pResample(PyObject *self, PyObject *args);


static PyMethodDef ZilanyCarney2009ANmethods[] = {
	{"ihc",ihc,METH_VARARGS},
	{"synapse",synapse,METH_VARARGS},
	{NULL, NULL}
};

void initZilanyCarney2009AN() {
	(void) Py_InitModule("ZilanyCarney2009AN",ZilanyCarney2009ANmethods);
	import_array();
}

/* This is the Python wrapper for ZilanyBruce 2006/2007 inner hear cell and auditory nerve model
   This wrapper is based on original MatLab(c) file with few minor corrections.
   * I've removed from code everything connected to the repetition. Please form stimulus if you need repetitive sound.  
   * Stimulus duration is calculated inside function
*/
PyObject *ihc(PyObject *self, PyObject *args){

	PyArrayObject *Vecin, *Vecout;
	double *vecin, *vecout;

	
	double *px, cf, tdres, reptime, cohc, cihc;
	int    pxbins, nrep, lp, outsize, totalstim;
    double *ihcout;
		
	/* Check with individual input arguments */
	if( !PyArg_ParseTuple(args,"O!didddd",
	&PyArray_Type, &Vecin,  	//(1)			the stimulus
	&cf, &nrep, &tdres,		//(2) (3) (4)	CF, number of stimulus repetitions, 1/sampling rate in Hz
	&reptime, &cohc, &cihc)//(5) (6) (7)	stimulus duration in seconds*2(?), impairment in the OHC, impairment in the IHC
//	&PyArray_Type, &RnD)
	  ||  Vecin == NULL ) return NULL;

	if( Vecin->descr->type_num != NPY_DOUBLE  || Vecin->nd != 1){
		PyErr_SetString( PyExc_ValueError ,"It isn\'t one dimensional array of FOLAT type." );
		return NULL;
	}
	if( (pxbins = Vecin->dimensions[0]) < 3){
		PyErr_Format( PyExc_ValueError ,"input vector size ( %d ) too small\n",pxbins);
		return NULL;
	}
	vecin = (double*)Vecin->data;
	
	
	if ((cf<80)|(cf>40e3)){
		PyErr_Format( PyExc_ValueError ,"cf (= %1.1f Hz) must be between 80 Hz and 40 kHz\n",cf);
		return NULL;
    }
	
	if (nrep<1){
		PyErr_SetString( PyExc_ValueError ,"nrep must be greater that one\n");
		return NULL;
	}
	/* duration of stimulus = pxbins*tdres */
	if ( (reptime-pxbins*tdres) > 1e-5){
		fprintf(stderr,"%g - %d * %g = %g > 1e-6\n",reptime,pxbins,tdres,(reptime-pxbins*tdres));
		PyErr_Format( PyExc_ValueError ,"reptime should be equal to or longer than the stimulus duration. (= %f > 1e-6)\n",(reptime-pxbins*tdres));
		return NULL;
	}
	
    /* impairment in the OHC  */
	if ((cohc<0)|(cohc>1)){
		PyErr_Format( PyExc_ValueError ,"cohc (= %1.1f) must be between 0 and 1\n",cohc);
		return NULL;
	}

	/* impairment in the IHC  */
	if ((cihc<0)|(cihc>1))
	{
		PyErr_Format( PyExc_ValueError ,"cihc (= %1.1f) must be between 0 and 1\n",cihc);
		return NULL;
	}
	
	/* Calculate number of samples for total repetition time */
	totalstim = (int)ceil((reptime*1e3)/(tdres*1e3));    

	if ( (px = (double*)calloc(totalstim,sizeof(double)) ) == NULL){
		 PyErr_Format( PyExc_ValueError ,"Cannot allocate memory for temporal buffer (size =  %dx4)\n",totalstim);
		 return NULL;
	}

	/* Put stimulus waveform into pressure waveform */
	for (lp=0; lp<pxbins; lp++)
			px[lp] = vecin[lp];
	
	/* Create an array for the return argument */
	
    outsize = totalstim*nrep;
	Vecout	= (PyArrayObject*) PyArray_FromDims(1,&outsize,NPY_DOUBLE);
	/* Assign pointers to the outputs */
	ihcout  = (double*)Vecout->data;
	/* run the model */
	int retval = IHCAN(px,cf,nrep,tdres,totalstim,cohc,cihc,ihcout);
	free(px);
	if (retval){
		PyErr_Format( PyExc_ValueError ,"IHCAN returns error value %d\n",retval);
		return NULL;
	}
	return PyArray_Return(Vecout);
}

PyObject *synapse(PyObject *self, PyObject *args)
{
	double *px, cf, tdres;
	int fibertype, implnt;
	int    nrep, pxbins, lp, outsize[2], totalstim;

        
    double *synout, *psth;
   	
	PyArrayObject *Vecin, *Vecout;
		
	/* Check with individual input arguments */
	if( !PyArg_ParseTuple(args,"O!didii",
	&PyArray_Type, &Vecin,  	//(0)			the stimulus
	&cf, &nrep, &tdres,			//(1) (2) (3)	CF, number of stimulus repetitions, 1/sampling rate in Hz
	&fibertype, &implnt)		//(4) (5)	spontaneous rate of the fiber, actual/approximate implementation of the power-law functions
	  ||  Vecin == NULL ) return NULL;

	if( Vecin->descr->type_num != NPY_DOUBLE  || Vecin->nd != 1){
		PyErr_SetString( PyExc_ValueError ,"It isn\'t one dimensional array of FOLAT type." );
		return NULL;
	}
	
	if ((cf<80)|(cf>40e3))
	{
		PyErr_Format( PyExc_ValueError ,"cf (= %1.1f Hz) must be between 80 Hz and 40 kHz\n",cf);
		return NULL;
	}
	
	if (nrep<1){
		PyErr_Format( PyExc_ValueError ,"nrep must be greater that 0.\n");
		return NULL;
	}


	//* Calculate number of samples for total repetition time 
	pxbins = Vecin->dimensions[0];
	double *vecin = (double*)Vecin->data;
	totalstim = (int)floor(pxbins/nrep);    
	long msize;
    px = (double*)calloc(msize = (long)totalstim*nrep,sizeof(double)); 
    memset(px,0,msize*sizeof(double) );

	//* Put stimulus waveform into pressure waveform 
    
   	for (lp=0; lp<pxbins; lp++)
			px[lp] = vecin[lp];
	
	//* Create an array for the return argument 
    
	PyArrayObject *Synout = (PyArrayObject*) PyArray_FromDims(1,&totalstim,NPY_DOUBLE);
	PyArrayObject *Plhs   = (PyArrayObject*) PyArray_FromDims(1,&totalstim,NPY_DOUBLE);
		
	//* Assign pointers to the outputs 
	
	synout	= (double*) Synout->data;
    psth	= (double*) Plhs->data;
			
	//* run the model 

	//mexPrintf("catmodel: Zilany, Bruce, Nelson, and Carney : Cat Auditory Nerve Model\n");
	long int spikenumber = SingleAN(px,cf,nrep,tdres,totalstim,(double)fibertype,implnt,synout,psth);
	if ( spikenumber < 0 ) return NULL;
	PyArray_Dims newdims;
	newdims.len=1;
	newdims.ptr = &spikenumber;
	
	//if( (Plhs = (PyArrayObject*) PyArray_Resize(Plhs, &newdims, 1, NPY_CORDER)) == NULL ) return NULL;
	free(px);
	PyObject* tuple = PyTuple_New(3);
	if ( tuple == NULL) return NULL;
	if ( PyTuple_SetItem(tuple,0,(PyObject*)Synout)) return NULL;
	if ( PyTuple_SetItem(tuple,1,(PyObject*)Plhs)) return NULL;
	if ( PyTuple_SetItem(tuple,2,PyInt_FromLong(spikenumber)) ) return NULL;
	
	return tuple;
}


