/*
   This is Version 3 of the public distribution of the code for the auditory
   periphery model of:

    Zilany, M.S.A., Bruce, I.C., Nelson, P.C., and Carney, L.H. (2009). "A Phenomenological
        model of the synapse between the inner hair cell and auditory nerve : Long-term adaptation 
        with power-law dynamics," Journal of the Acoustical Society of America 126(5): 2390-2412.        

   Please cite this paper if you publish any research
   results obtained with this code or any modified versions of this code.

   See the file readme.txt for details of compiling and running the model.  
   
   %%% (C) Muhammad S.A. Zilany (msazilany@gmail.com), Ian C. Bruce, Paul C. Nelson, and laurel H. Carney October 2008 %%%
   
*/

#include <Python.h>
#include <numpy/arrayobject.h>

/* #include <iostream.h> */

#include "complex.hpp"

#define MAXSPIKES 1000000
#ifndef TWOPI
#define TWOPI 6.28318530717959
#endif

#ifndef __max
#define __max(a,b) (((a) > (b))? (a): (b))
#endif

#ifndef __min
#define __min(a,b) (((a) < (b))? (a): (b))
#endif

/* RTH: Declarations of STATIC functions used in the program */
static int Synapse(double *, double, double, int, int, double, int, double, double *);
static int SpikeGenerator(double *, double, int, int, double *);


/* RTH: the core function for ZilanyBruceNelsonCarney 2009inner hear cell and auditory nerve  
        in this version function returns int value: 0 if it finishes normal or Error Code.
*/

int SingleAN(double *px, double cf, int nrep, double tdres, int totalstim, double fibertype, int implnt, double *synout, double *psth)
{	
        	
	/*variables for the signal-path, control-path and onward */
	double *synouttmp,*sptime;

	int    i,nspikes,ipst;
	double I,spont;
    double sampFreq = 10e3; /* Sampling frequency used in the synapse */
        
    
    /* Allocate dynamic memory for the temporary variables */
    long unsigned msize;
/*DB*///    fprintf(stderr, "SingleAN  allocation memory");
    if( (synouttmp  = (double*)calloc(msize = totalstim*nrep,sizeof(double)) ) == NULL ) return -1;
    memset(synouttmp,0,msize*sizeof(double) );
    if( (sptime  = (double*)calloc(msize = (long) ceil(totalstim*tdres*nrep/0.00075),sizeof(double)) ) == NULL ) return -1;
    memset(sptime,0,msize*sizeof(double) );
/*DB*/ //   fprintf(stderr,"done\n");
	   
    /* Spontaneous Rate of the fiber corresponding to Fibertype */    
    if (fibertype==1) spont = 0.1;
    if (fibertype==2) spont = 5.0;
    if (fibertype==3) spont = 100.0;
    
    /*====== Run the synapse model ======*/    
    if( (I = Synapse(px, tdres, cf, totalstim, nrep, spont, implnt, sampFreq, synouttmp) ) < 0) return -1;
            
    /* Wrapping up the unfolded (due to no. of repetitions) Synapse Output */
    for(i = 0; i <I ; i++)
	{       
		ipst = (int) (fmod(i,totalstim));
        synout[ipst] = synout[ipst] + synouttmp[i]/nrep;       
	};    
    /*======  Spike Generations ======*/
    
	if( (nspikes = SpikeGenerator(synouttmp, tdres, totalstim, nrep, sptime) ) < 0 ) return -1;
	
	for(i = 0; i < nspikes; i++)
	{ 
		//RTH: We need only spike times without conversion to raster.
		psth[i] = sptime[i];
		//ipst = (int) (fmod(sptime[i],tdres*totalstim) / tdres);
        //psth[ipst] = psth[ipst] + 1;       
	};

    /* Freeing dynamic memory allocated earlier */

    free(sptime); free(synouttmp);
    //return 0;
    //RTH: returns number of spikes in vector
    return nspikes;

} /* End of the SingleAN function */

/* -------------------------------------------------------------------------------------------- */
/*  Synapse model: if the time resolution is not small enough, the concentration of
   the immediate pool could be as low as negative, at this time there is an alert message
   print out and the concentration is set at saturated level  */
/* --------------------------------------------------------------------------------------------*/
/*RTH: This is a helper variables and function.
 * Function setFuncPointers sets up pointers for resample function in scipy.signal library,
 * rand in numpu.random library and ffGn in ffGn.py module
 */
static PyObject *pResample = NULL, *pRand = NULL, *pFfGn = NULL; //pointers on functions
static int setFuncPointers(){
	PyObject *pName, *pModule, *pDic;
	if ( pFfGn == NULL || pRand == NULL || pResample == NULL){
		pName = PyString_FromString("ffGn");
		if( pName == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t setup string ffGn\n");
			return 1;
		}
		pModule = PyImport_Import(pName);
		Py_DECREF(pName);
		if( pModule == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t find module ffGn\n");
			return 1;
		}
		pDic = PyModule_GetDict(pModule);
		Py_DECREF(pModule);
		if( pDic == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t find dictionary in module ffGn\n");
			return 1;
		}
		pFfGn = PyDict_GetItemString(pDic, "ffGn");
		pRand = PyDict_GetItemString(pDic, "rand");
		pResample = PyDict_GetItemString(pDic, "resample");
		Py_DECREF(pDic);
		if( pFfGn == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t find function ffGn in the dictionary of ffGn\n");
			return 1;
		}
		if( pRand == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t find function  rand in the dictionary of ffGn\n");
			return 1;
		}
		if( pResample == NULL){
			PyErr_Format(PyExc_ReferenceError,"Couldn\'t find function  resample in the dictionary of ffGn\n");
			return 1;
		}
/*DB*/	//fprintf(stderr,"Have found resample\n");
/*DB*/	//fprintf(stderr,"rand has been found\n");
/*DB*/	//fprintf(stderr,"ffGn has been found\n");
	}
	import_array1(-1);
	return 0;
}

int Synapse(double *ihcout, double tdres, double cf, int totalstim, int nrep, double spont, int implnt, double sampFreq, double *synouttmp)
{    
    /* Initalize Variables */     
    int z, b;
    int resamp = (int) ceil(1/(tdres*sampFreq));
    double incr = 0.0; int delaypoint = floor(7500/(cf/1e3));   
    
    double alpha1, beta1, I1, alpha2, beta2, I2, binwidth;
    int    k,j,indx,i;    
    double synstrength,synslope,CI,CL,PG,CG,VL,PL,VI;
	double cf_factor,PImax,kslope,Ass,Asp,TauR,TauST,Ar_Ast,PTS,Aon,AR,AST,Prest,gamma1,gamma2,k1,k2;
	double VI0,VI1,alpha,beta,theta1,theta2,theta3,vsat,tmpst,tmp,PPI,CIlast,temp;
            
    double *sout1, *sout2, *synSampOut, *powerLawIn, *exponOut, *TmpSyn;            
    double *m1, *m2, *m3, *m4, *m5;
	double *n1, *n2, *n3;
    
    double *randNums;
    
    //mxArray	*IhcInputArray[3], *IhcOutputArray[1];
    double *sampIHC, *ihcDims;	  
    long unsigned msize;
    exponOut = (double*)calloc(msize = (long) ceil(totalstim*nrep),sizeof(double));
    memset(exponOut,0,msize*sizeof(double) );
    powerLawIn = (double*)calloc(msize = (long) ceil(totalstim*nrep+3*delaypoint),sizeof(double));
    memset(powerLawIn,0,msize*sizeof(double) );
    sout1 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(sout1,0,msize*sizeof(double) );
    sout2 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(sout2,0,msize*sizeof(double) );
    synSampOut  = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(synSampOut,0,msize*sizeof(double) );
    TmpSyn  = (double*)calloc(msize = (long) ceil(totalstim*nrep+2*delaypoint),sizeof(double));
    memset(TmpSyn,0,msize*sizeof(double) );
      
    m1 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(m1,0,msize*sizeof(double) );
    m2 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(m2,0,msize*sizeof(double) );
    m3  = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double)); 
    memset(m3,0,msize*sizeof(double) );
    m4 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(m4,0,msize*sizeof(double) );
    m5  = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double)); 
    memset(m5,0,msize*sizeof(double) );
    
    n1 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(n1,0,msize*sizeof(double) );
    n2 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));
    memset(n2,0,msize*sizeof(double) );
    n3 = (double*)calloc(msize = (long) ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq),sizeof(double));    
    memset(n3,0,msize*sizeof(double) );
	
    /*----------------------------------------------------------*/    
    /*------- Parameters of the Power-law function -------------*/
    /*----------------------------------------------------------*/ 
    binwidth = 1/sampFreq;
    alpha1 = 5e-6*100e3; beta1 = 5e-4; I1 =0;
    alpha2 = 1e-2*100e3; beta2 = 1e-1; I2 =0;       
    /*----------------------------------------------------------*/    
    /*------- Generating a random sequence ---------------------*/
    /*----------------------------------------------------------*/ 
    PyObject *arg1, *arg2, *arg3, *arg4;
    if ( pFfGn == NULL  && setFuncPointers() ){
		//PyErr_Format(PyExc_ValueError ,"Cannot bind function ffGN! Abort!" );
		return -1;
	}
/*DB*///(stderr,"Synmodel: Create random vector");	
    PyArrayObject *randVec = (PyArrayObject *)PyObject_CallFunctionObjArgs(pFfGn, 
		arg1 = PyInt_FromLong((long)ceil((totalstim*nrep+2*delaypoint)*tdres*sampFreq)),
		arg2 = PyFloat_FromDouble(1./sampFreq),
		arg3 = PyFloat_FromDouble(0.9), // Hurst index 
		arg4 = PyFloat_FromDouble(spont),
		NULL);
	Py_DECREF(arg1); Py_DECREF(arg2); Py_DECREF(arg3); Py_DECREF(arg4);
	if (randVec == NULL)return -1;
    randNums = (double*)randVec->data;
/*DB*///fprintf(stderr,"done\n");
    /*----------------------------------------------------------*/
    /*----- Double Exponential Adaptation ----------------------*/
    /*----------------------------------------------------------*/    
       if (spont==100) cf_factor = __min(800,pow(10,0.29*cf/1e3 + 0.7));
       if (spont==5)   cf_factor = __min(50,2.5e-4*cf*4+0.2);
       if (spont==0.1) cf_factor = __min(1.0,2.5e-4*cf*0.1+0.15);              
	         
	   PImax  = 0.6;                /* PI2 : Maximum of the PI(PI at steady state) */
       kslope = (1+50.0)/(5+50.0)*cf_factor*20.0*PImax;           
    	   
       Ass    = 300*TWOPI/2*(1+cf/10e3);    /* Steady State Firing Rate eq.10 */
       if (implnt==1) Asp = spont*5;   /* Spontaneous Firing Rate if actual implementation */
       if (implnt==0) Asp = spont*4.1; /* Spontaneous Firing Rate if approximate implementation */
       TauR   = 2e-3;               /* Rapid Time Constant eq.10 */
       TauST  = 60e-3;              /* Short Time Constant eq.10 */
       Ar_Ast = 6;                  /* Ratio of Ar/Ast */
       PTS    = 3;                  /* Peak to Steady State Ratio, characteristic of PSTH */
   
       /* now get the other parameters */
       Aon    = PTS*Ass;                          /* Onset rate = Ass+Ar+Ast eq.10 */
       AR     = (Aon-Ass)*Ar_Ast/(1+Ar_Ast);      /* Rapid component magnitude: eq.10 */
       AST    = Aon-Ass-AR;                       /* Short time component: eq.10 */
       Prest  = PImax/Aon*Asp;                    /* eq.A15 */
       //printf("Prest=%g; Aon=%g; Asp=%g\n",Prest,Aon,Asp);
       CG  = (Asp*(Aon-Asp))/(Aon*Prest*(1-Asp/Ass));    /* eq.A16 */
       gamma1 = CG/Asp;                           /* eq.A19 */
       gamma2 = CG/Ass;                           /* eq.A20 */
       k1     = -1/TauR;                          /* eq.8 & eq.10 */
       k2     = -1/TauST;                         /* eq.8 & eq.10 */
               /* eq.A21 & eq.A22 */
       VI0    = (1-PImax/Prest)/(gamma1*(AR*(k1-k2)/CG/PImax+k2/Prest/gamma1-k2/PImax/gamma2));
       VI1    = (1-PImax/Prest)/(gamma1*(AST*(k2-k1)/CG/PImax+k1/Prest/gamma1-k1/PImax/gamma2));
       VI  = (VI0+VI1)/2;
       alpha  = gamma2/k1/k2;       /* eq.A23,eq.A24 or eq.7 */
       beta   = -(k1+k2)*alpha;     /* eq.A23 or eq.7 */
       theta1 = alpha*PImax/VI; 
       theta2 = VI/PImax;
       theta3 = gamma2-1/PImax;
  
       PL  = ((beta-theta2*theta3)/theta1-1)*PImax;  /* eq.4' */
       PG  = 1/(theta3-1/PL);                        /* eq.5' */
       VL  = theta1*PL*PG;                           /* eq.3' */
       CI  = Asp/Prest;                              /* CI at rest, from eq.A3,eq.A12 */
       CL  = CI*(Prest+PL)/PL;                       /* CL at rest, from eq.1 */
		
       if(kslope>=0)  vsat = kslope+Prest;                
       tmpst  = log(2)*vsat/Prest;
       if(tmpst<400) synstrength = log(exp(tmpst)-1);
       else synstrength = tmpst;
       synslope = Prest/log(2)*synstrength;
       
       k = 0;     
       for (indx=0; indx<totalstim*nrep; ++indx)
       {
            tmp = synstrength*(ihcout[indx]);
            //printf("tmp=%g//",tmp);
            if(tmp<400) tmp = log(1+exp(tmp));
            //printf("tmp=%g//",tmp);
            PPI = synslope/synstrength*tmp;
            //printf("PPI=%g,synslope=%g,synstrength=%g\n",PPI,synslope,synstrength);
         
            CIlast = CI; 
            CI = CI + (tdres/VI)*(-PPI*CI + PL*(CL-CI));
            CL = CL + (tdres/VL)*(-PL*(CL - CIlast) + PG*(CG - CL));
            if(CI<0)
            {
                temp = 1./PG+1./PL+1./PPI;
                CI = CG/(PPI*temp);
                CL = CI*(PPI+PL)/PL;
            };
            exponOut[k] = CI*PPI;
            //printf("%g\t%g\t%g\t%g\t%g\t%g\n",exponOut[k],CI,PPI,PL,PG,ihcout[indx]);
            k=k+1;
        }                 
        for (k=0; k<delaypoint; k++)
			powerLawIn[k] = exponOut[0];    
        for (k=delaypoint; k<totalstim*nrep+delaypoint; k++)
			powerLawIn[k] = exponOut[k-delaypoint];
        for (k=totalstim*nrep+delaypoint; k<totalstim*nrep+3*delaypoint; k++)
			powerLawIn[k] = powerLawIn[k-1];         
   /*----------------------------------------------------------*/ 
   /*------ Downsampling to sampFreq (Low) sampling rate ------*/   
   /*----------------------------------------------------------*/
    if ( pResample == NULL  && setFuncPointers() ){
		//PyErr_Format(PyExc_ValueError ,"Cannot bind function resample! Abort!" );
		return -1;
	}
/*DB*///fprintf(stderr,"create array.... k=%d ",k);	
   PyArrayObject* Ihcin	= (PyArrayObject*) PyArray_FromDims(1,&k,NPY_DOUBLE); 
/*DB*///fprintf(stderr,"done\n");	
   if (Ihcin == NULL){
		//PyErr_Format(PyExc_ValueError ,"Cannot create Array! Abort!" );
		return -1;
   }
   double *d0tmp = (double*)Ihcin->data, *dItmp = powerLawIn;
/*DB*///fprintf(stderr,"copy data the C code\n");	
    for (i=0;i<k;++i,++d0tmp, ++dItmp)*d0tmp = *dItmp;
    //fprintf(stderr,"\n===\nk=%d,resamp=%d,k/resamp=%d\n===\n",k,resamp,k/resamp);
    PyArrayObject *outVec = (PyArrayObject *)PyObject_CallFunctionObjArgs(pResample, 
		arg1 = (PyObject*)Ihcin,
		arg2 = PyFloat_FromDouble((double)floor(k/resamp)),
		NULL);
/*DB*///fprintf(stderr,"Resample was passed in C code\n");	
	Py_DECREF(arg1); Py_DECREF(arg2);
	if (outVec == NULL)	return -1;

    sampIHC = (double*)outVec->data;
/*DB*///printf("outVec.size=%d, randVec.size=%d, resamp=%d,k=%d\n",outVec->dimensions[0],randVec->dimensions[0],resamp,k);    
    
    free(powerLawIn); free(exponOut);
   /*----------------------------------------------------------*/
   /*----- Running Power-law Adaptation -----------------------*/     
   /*----------------------------------------------------------*/
    k = 0;
    for (indx=0; indx<floor((totalstim*nrep+2*delaypoint)*tdres*sampFreq); indx++)
    {
    	//printf("%d ",k);
          sout1[k]  = __max( 0, sampIHC[indx*2] + randNums[indx]- alpha1*I1); 
          /* sout1[k]  = __max( 0, sampIHC[indx] - alpha1*I1); */   /* No fGn condition */
          sout2[k]  = __max( 0, sampIHC[indx*2] - alpha2*I2); 
                                   
         if (implnt==1)    /* ACTUAL Implementation */
         {
              I1 = 0; I2 = 0; 
              for (j=0; j<k+1; ++j)
                  {
                      I1 += (sout1[j])*binwidth/((k-j)*binwidth + beta1);
                      I2 += (sout2[j])*binwidth/((k-j)*binwidth + beta2);              
                   }
         } /* end of actual */
              
         if (implnt==0)    /* APPROXIMATE Implementation */
         {              
                if (k==0)
                {
                    n1[k] = 1.0e-3*sout2[k];
                    n2[k] = n1[k]; n3[0]= n2[k];
                }
                else if (k==1)
                {
                    n1[k] = 1.992127932802320*n1[k-1]+ 1.0e-3*(sout2[k] - 0.994466986569624*sout2[k-1]);
                    n2[k] = 1.999195329360981*n2[k-1]+ n1[k] - 1.997855276593802*n1[k-1];
                    n3[k] = -0.798261718183851*n3[k-1]+ n2[k] + 0.798261718184977*n2[k-1];
                }
                else
                {			
                    n1[k] = 1.992127932802320*n1[k-1] - 0.992140616993846*n1[k-2]+ 1.0e-3*(sout2[k] - 0.994466986569624*sout2[k-1] + 0.000000000002347*sout2[k-2]);
                    n2[k] = 1.999195329360981*n2[k-1] - 0.999195402928777*n2[k-2]+n1[k] - 1.997855276593802*n1[k-1] + 0.997855827934345*n1[k-2];
                    n3[k] =-0.798261718183851*n3[k-1] - 0.199131619873480*n3[k-2]+n2[k] + 0.798261718184977*n2[k-1] + 0.199131619874064*n2[k-2];
                }   
                I2 = n3[k];       

                if (k==0)
                {
                    m1[k] = 0.2*sout1[k];
                    m2[k] = m1[k];	m3[k] = m2[k];			
                    m4[k] = m3[k];	m5[k] = m4[k];
                }
                else if (k==1)
                {
                    m1[k] = 0.491115852967412*m1[k-1] + 0.2*(sout1[k] - 0.173492003319319*sout1[k-1]);
                    m2[k] = 1.084520302502860*m2[k-1] + m1[k] - 0.803462163297112*m1[k-1];
                    m3[k] = 1.588427084535629*m3[k-1] + m2[k] - 1.416084732997016*m2[k-1];
                    m4[k] = 1.886287488516458*m4[k-1] + m3[k] - 1.830362725074550*m3[k-1];
                    m5[k] = 1.989549282714008*m5[k-1] + m4[k] - 1.983165053215032*m4[k-1];
                }        
                else
                {
                    m1[k] = 0.491115852967412*m1[k-1] - 0.055050209956838*m1[k-2]+ 0.2*(sout1[k]- 0.173492003319319*sout1[k-1]+ 0.000000172983796*sout1[k-2]);
                    m2[k] = 1.084520302502860*m2[k-1] - 0.288760329320566*m2[k-2] + m1[k] - 0.803462163297112*m1[k-1] + 0.154962026341513*m1[k-2];
                    m3[k] = 1.588427084535629*m3[k-1] - 0.628138993662508*m3[k-2] + m2[k] - 1.416084732997016*m2[k-1] + 0.496615555008723*m2[k-2];
                    m4[k] = 1.886287488516458*m4[k-1] - 0.888972875389923*m4[k-2] + m3[k] - 1.830362725074550*m3[k-1] + 0.836399964176882*m3[k-2];
                    m5[k] = 1.989549282714008*m5[k-1] - 0.989558985673023*m5[k-2] + m4[k] - 1.983165053215032*m4[k-1] + 0.983193027347456*m4[k-2];
                }   
                I1 = m5[k]; 
            } /* end of approximate implementation */
        
        synSampOut[k] = sout1[k] + sout2[k];
        //printf("%d\t%g\t%g\t%g%g\t%g\n",k,sampIHC[indx],randNums[indx],synSampOut[k],sout1[k],sout2[k]);          
        k = k+1;                  
      }   /* end of all samples */
      free(sout1); free(sout2);  
      free(m1); free(m2); free(m3); free(m4); free(m5); free(n1); free(n2); free(n3); 
    /*----------------------------------------------------------*/    
    /*----- Upsampling to original (High 100 kHz) sampling rate --------*/  
    /*----------------------------------------------------------*/    
    for(z=0; z<k-1; ++z)
    {    
        incr = (synSampOut[z+1]-synSampOut[z])/resamp;
        //printf("%d\t%g\n",z,synSampOut[z]);
        for(b=0; b<resamp; ++b)
        {
            TmpSyn[z*resamp+b] = synSampOut[z]+ b*incr; 
        }        
    }      
    for (i=0;i<totalstim*nrep;++i)
        synouttmp[i] = TmpSyn[i+delaypoint];      
    
    free(synSampOut); free(TmpSyn);   
	Py_DECREF(randVec); 
	Py_DECREF(outVec);
    return((long) ceil(totalstim*nrep));
}    
/* ------------------------------------------------------------------------------------ */
/* Pass the output of Synapse model through the Spike Generator */

/* The spike generator now uses a method coded up by B. Scott Jackson (bsj22@cornell.edu) 
   Scott's original code is available from Laurel Carney's web site at:
   http://www.urmc.rochester.edu/smd/Nanat/faculty-research/lab-pages/LaurelCarney/auditory-models.cfm
*/

int SpikeGenerator(double *synouttmp, double tdres, int totalstim, int nrep, double *sptime) 
{  
   	double  c0,s0,c1,s1,dead;
    int     nspikes,k,NoutMax,Nout,deadtimeIndex,randBufIndex;      
    double	deadtimeRnd, endOfLastDeadtime, refracMult0, refracMult1, refracValue0, refracValue1;
    double	Xsum, unitRateIntrvl, countTime, DT;    
    
    double *randNums, *randDims;    
    
    c0      = 0.5;
	s0      = 0.001;
	c1      = 0.5;
	s1      = 0.0125;
    dead    = 0.00075;
    
    DT = totalstim * tdres * nrep;  /* Total duration of the rate function */
    Nout = 0;
    NoutMax = (long) ceil(totalstim*nrep*tdres/dead);    
       
    PyObject *arg1;
	PyArrayObject *randVec = (PyArrayObject *) PyObject_CallFunctionObjArgs(pRand, 
		arg1 = PyInt_FromLong( (long) NoutMax+1 ),
		NULL);
	Py_DECREF(arg1);
	if ( randVec == NULL ) return -1;
    randNums = (double *) randVec->data;
    randBufIndex = 0;
    
	/* Calculate useful constants */
	deadtimeIndex = (long) floor(dead/tdres);  /* Integer number of discrete time bins within deadtime */
	deadtimeRnd = deadtimeIndex*tdres;		   /* Deadtime rounded down to length of an integer number of discrete time bins */

	refracMult0 = 1 - tdres/s0;  /* If y0(t) = c0*exp(-t/s0), then y0(t+tdres) = y0(t)*refracMult0 */
	refracMult1 = 1 - tdres/s1;  /* If y1(t) = c1*exp(-t/s1), then y1(t+tdres) = y1(t)*refracMult1 */

	/* Calculate effects of a random spike before t=0 on refractoriness and the time-warping sum at t=0 */
    endOfLastDeadtime = __max(0,log(randNums[randBufIndex++]) / synouttmp[0] + dead);  /* End of last deadtime before t=0 */
    refracValue0 = c0*exp(endOfLastDeadtime/s0);     /* Value of first exponential in refractory function */
	refracValue1 = c1*exp(endOfLastDeadtime/s1);     /* Value of second exponential in refractory function */
	Xsum = synouttmp[0] * (-endOfLastDeadtime + c0*s0*(exp(endOfLastDeadtime/s0)-1) + c1*s1*(exp(endOfLastDeadtime/s1)-1));  
        /* Value of time-warping sum */
		/*  ^^^^ This is the "integral" of the refractory function ^^^^ (normalized by 'tdres') */

	/* Calculate first interspike interval in a homogeneous, unit-rate Poisson process (normalized by 'tdres') */
    unitRateIntrvl = -log(randNums[randBufIndex++])/tdres;  
	    /* NOTE: Both 'unitRateInterval' and 'Xsum' are divided (or normalized) by 'tdres' in order to reduce calculation time.  
		This way we only need to divide by 'tdres' once per spike (when calculating 'unitRateInterval'), instead of 
		multiplying by 'tdres' once per time bin (when calculating the new value of 'Xsum').                         */

	countTime = tdres;
	for (k=0; (k<totalstim*nrep) && (countTime<DT); ++k, countTime+=tdres, refracValue0*=refracMult0, refracValue1*=refracMult1)  /* Loop through rate vector */
	{
		if (synouttmp[k]>0)  /* Nothing to do for non-positive rates, i.e. Xsum += 0 for non-positive rates. */
		{
		  Xsum += synouttmp[k]*(1 - refracValue0 - refracValue1);  /* Add synout*(refractory value) to time-warping sum */
			
			if ( Xsum >= unitRateIntrvl )  /* Spike occurs when time-warping sum exceeds interspike "time" in unit-rate process */
			{
				sptime[Nout] = countTime; Nout = Nout+1;								
				unitRateIntrvl = -log(randNums[randBufIndex++]) /tdres; 
                 Xsum = 0;
				
			    /* Increase index and time to the last time bin in the deadtime, and reset (relative) refractory function */
				k += deadtimeIndex;
				countTime += deadtimeRnd;
				refracValue0 = c0;
				refracValue1 = c1;
			}
		}
	} /* End of rate vector loop */			
            
    //mxDestroyArray(randInputArray[0]); mxDestroyArray(randOutputArray[0]);
    Py_DECREF(randVec);
	nspikes = Nout;  /* Number of spikes that occurred. */
	return(nspikes);
}
