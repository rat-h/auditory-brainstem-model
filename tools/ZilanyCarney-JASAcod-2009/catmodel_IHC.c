/* This is Version 1 of the public distribution of the code for the auditory
   periphery model of:

        Zilany, M. S. A. and Bruce, I. C. (2007). "Representation of the vowel
        /eh/ in normal and impaired auditory nerve fibers: Model predictions of
        responses in cats," Journal of the Acoustical Society of America
        122(1):402-417.    

        Zilany, M. S. A. and Bruce, I. C. (2006). "Modeling auditory-nerve
        responses for high sound pressure levels in the normal and impaired
        auditory periphery," Journal of the Acoustical Society of
        America 120(3):1446-1466.

   Please cite these papers if you publish any research
   results obtained with this code or any modified versions of this code.

   See the file readme.txt for details of compiling and running the model.  
   
   %%% � Ian C. Bruce (ibruce@ieee.org) and M. S. Arefeen Zilany, June 2006 %%%

*/

//Modified and optimized by Ruben Tikidji-Hamburayn <rth@nisms.krinc.ru> <rtikid@lsuhsc.edu>
//                      and Timur Pinin <timpin@rambler.ru>

#include <Python.h>
#include <numpy/arrayobject.h>

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

/* Declarations of static functions used in the program */
static double C1ChirpFilt(double, double,double, int, double, double);
static double C2ChirpFilt(double, double,double, int, double, double);
double WbGammaTone(double, double, double, int, double, double, int);

static double Get_tauwb(double, int, double *, double *);
static double Get_taubm(double, double, double *, double *, double *);
static double gain_groupdelay(double, double, double, double, int *);
static double delay_cat(double cf);

static double OhcLowPass(double, double, double, int, double, int);
static double IhcLowPass(double, double, double, int, double, int);
static double Boltzman(double, double, double, double, double);
static double NLafterohc(double, double, double, double);
static double ControlSignal(double, double, double, double, double);

static double NLogarithm(double, double, double, double);


//int IHCAN(double *px, double cf, int nrep, double tdres, int totalstim,
                //double cohc, double cihc, double *ihcout)
//{	
    
    ///*variables for middle-ear model */
	//double megainmax=43;
    //double *mey1, *mey2, *mey3, meout,c1filterouttmp,c2filterouttmp,c1vihctmp,c2vihctmp;
    //double fp,C,m11,m12,m21,m22,m23,m24,m25,m26,m31,m32,m33,m34,m35,m36;
	
	///*variables for the signal-path, control-path and onward */
	//double *ihcouttmp,*tmpgain;
	//int    grd;

    //double bmplace,centerfreq,gain,taubm,ratiowb,bmTaubm,fcohc,TauWBMax,TauWBMin,tauwb;
    //double Taumin[1],Taumax[1],bmTaumin[1],bmTaumax[1],ratiobm[1],lasttmpgain,wbgain,ohcasym,ihcasym,delay;
	//int    i,n,delaypoint,grdelay[1],bmorder,wborder;
	//double wbout1,wbout,ohcnonlinout,ohcout,tmptauc1,tauc1,rsigma,wb_gain;
            
    ///* Declarations of the functions used in the program */
	//double C1ChirpFilt(double, double,double, int, double, double);
	//double C2ChirpFilt(double, double,double, int, double, double);
    //double WbGammaTone(double, double, double, int, double, double, int);

    //double Get_tauwb(double, int, double *, double *);
	//double Get_taubm(double, double, double *, double *, double *);
    //double gain_groupdelay(double, double, double, double, int *);
    //double delay_cat(double cf);

    //double OhcLowPass(double, double, double, int, double, int);
    //double IhcLowPass(double, double, double, int, double, int);
	//double Boltzman(double, double, double, double, double);
    //double NLafterohc(double, double, double, double);
	//double ControlSignal(double, double, double, double, double);

    //double NLogarithm(double, double, double, double);
    
    ///* Allocate dynamic memory for the temporary variables */
	//ihcouttmp  = (double*)calloc(totalstim*nrep,sizeof(double));
	    
	//mey1 = (double*)calloc(totalstim,sizeof(double));
	//mey2 = (double*)calloc(totalstim,sizeof(double));
	//mey3 = (double*)calloc(totalstim,sizeof(double));

	//tmpgain = (double*)calloc(totalstim,sizeof(double));
    
	///** Calculate the location on basilar membrane from CF */	
    
	//bmplace = 11.9 * log10(0.80 + cf / 456.0); 
    
	///** Calculate the center frequency for the control-path wideband filter
	    //from the location on basilar membrane */
	
	//centerfreq = 456.0*(pow(10,(bmplace+1.2)/11.9)-0.80); /* shift the center freq */
    
	///*==================================================================*/
	///*====== Parameters for the gain ===========*/
	//gain = 52/2*(tanh(2.2*log10(cf/0.6e3)+0.15)+1);
    ///*gain = 52/2*(tanh(2.2*log10(cf/1e3)+0.15)+1);*/
    //if(gain>60) gain = 60;  
    //if(gain<15) gain = 15;
	///*====== Parameters for the control-path wideband filter =======*/
	//bmorder = 3;
	//Get_tauwb(cf,bmorder,Taumax,Taumin);
	//taubm   = cohc*(Taumax[0]-Taumin[0])+Taumin[0];
	//ratiowb = Taumin[0]/Taumax[0];
	///*====== Parameters for the signal-path C1 filter ======*/
	//Get_taubm(cf,Taumax[0],bmTaumax,bmTaumin,ratiobm);
	//bmTaubm  = cohc*(bmTaumax[0]-bmTaumin[0])+bmTaumin[0];
	//fcohc    = bmTaumax[0]/bmTaubm;
    ///*====== Parameters for the control-path wideband filter =======*/
	//wborder  = 3;
    //TauWBMax = Taumin[0]+0.2*(Taumax[0]-Taumin[0]);
	//TauWBMin = TauWBMax/Taumax[0]*Taumin[0];
    //tauwb    = TauWBMax+(bmTaubm-bmTaumax[0])*(TauWBMax-TauWBMin)/(bmTaumax[0]-bmTaumin[0]);
	
	//wbgain = gain_groupdelay(tdres,centerfreq,cf,tauwb,grdelay);
	//tmpgain[0]   = wbgain; 
	//lasttmpgain  = wbgain;
  	///*===============================================================*/
    ///* Nonlinear asymmetry of OHC function and IHC C1 transduction function*/
	//ohcasym  = 7.0;    
	//ihcasym  = 3.0;
  	///*===============================================================*/
    ///*===============================================================*/
    ///* Prewarping and related constants for the middle ear */
     //fp = 1e3;  /* prewarping frequency 1 kHz */
     //C  = TWOPI*fp/tan(TWOPI/2*fp*tdres);
	 //m11 = C/(C + 693.48);                    m12 = (693.48 - C)/C;
	 //m21 = 1/(pow(C,2) + 11053*C + 1.163e8);  m22 = -2*pow(C,2) + 2.326e8;    m23 = pow(C,2) - 11053*C + 1.163e8; 
	 //m24 = pow(C,2) + 1356.3*C + 7.4417e8;    m25 = -2*pow(C,2) + 14.8834e8;  m26 = pow(C,2) - 1356.3*C + 7.4417e8;
	 //m31 = 1/(pow(C,2) + 4620*C + 909059944); m32 = -2*pow(C,2) + 2*909059944; m33 = pow(C,2) - 4620*C + 909059944;
	 //m34 = 5.7585e5*C + 7.1665e7;             m35 = 14.333e7;                 m36 = 7.1665e7 - 5.7585e5*C;
	 
  	//for (n=0;n<totalstim;n++) /* Start of the loop */
    //{    
        //if (n==0)  /* Start of the middle-ear filtering section  */
		//{
	    	//mey1[0]  = m11*px[0];
            //mey2[0]  = mey1[0]*m24*m21;
            //mey3[0]  = mey2[0]*m34*m31;
            //meout = mey3[0]/megainmax ;
        //}
            
        //else if (n==1)
		//{
            //mey1[1]  = m11*(-m12*mey1[0] + px[1]       - px[0]);
			//mey2[1]  = m21*(-m22*mey2[0] + m24*mey1[1] + m25*mey1[0]);
            //mey3[1]  = m31*(-m32*mey3[0] + m34*mey2[1] + m35*mey2[0]);
            //meout = mey3[1]/megainmax;
		//}
	    //else 
		//{
            //mey1[n]  = m11*(-m12*mey1[n-1]  + px[n]         - px[n-1]);
            //mey2[n]  = m21*(-m22*mey2[n-1] - m23*mey2[n-2] + m24*mey1[n] + m25*mey1[n-1] + m26*mey1[n-2]);
            //mey3[n]  = m31*(-m32*mey3[n-1] - m33*mey3[n-2] + m34*mey2[n] + m35*mey2[n-1] + m36*mey2[n-2]);
            //meout = mey3[n]/megainmax;
		//}; 	/* End of the middle-ear filtering section */   
     
		///* Control-path filter */

        //wbout1 = WbGammaTone(meout,tdres,centerfreq,n,tauwb,wbgain,wborder);
        //wbout  = pow((tauwb/TauWBMax),wborder)*wbout1*10e3*__max(1,cf/5e3);
  
        //ohcnonlinout = Boltzman(wbout,ohcasym,12.0,5.0,5.0); /* pass the control signal through OHC Nonlinear Function */
		//ohcout = OhcLowPass(ohcnonlinout,tdres,600,n,1.0,2);/* lowpass filtering after the OHC nonlinearity */
        
		//tmptauc1 = NLafterohc(ohcout,bmTaumin[0],bmTaumax[0],ohcasym); /* nonlinear function after OHC low-pass filter */
		//tauc1    = cohc*(tmptauc1-bmTaumin[0])+bmTaumin[0];  /* time -constant for the signal-path C1 filter */
		//rsigma   = 1/tauc1-1/bmTaumax[0]; /* shift of the location of poles of the C1 filter from the initial positions */

		//if (1/tauc1<0.0) fprintf(stderr,"The poles are in the right-half plane; system is unstable.\n");

		//tauwb = TauWBMax+(tauc1-bmTaumax[0])*(TauWBMax-TauWBMin)/(bmTaumax[0]-bmTaumin[0]);

	    //wb_gain = gain_groupdelay(tdres,centerfreq,cf,tauwb,grdelay);
		
		//grd = grdelay[0]; 

        //if ((grd+n)<totalstim)
	         //tmpgain[grd+n] = wb_gain;

        //if (tmpgain[n] == 0)
			//tmpgain[n] = lasttmpgain;	
		
		//wbgain      = tmpgain[n];
		//lasttmpgain = wbgain;
	 		        
        ///*====== Signal-path C1 filter ======*/
         
		 //c1filterouttmp = C1ChirpFilt(meout, tdres, cf, n, bmTaumax[0], rsigma); /* C1 filter output */

	 
        ///*====== Parallel-path C2 filter ======*/

		 //c2filterouttmp  = C2ChirpFilt(meout, tdres, cf, n, bmTaumax[0], 1/ratiobm[0]); /* parallel-filter output*/

	    ///*=== Run the inner hair cell (IHC) section: NL function and then lowpass filtering ===*/

        //c1vihctmp  = NLogarithm(cihc*c1filterouttmp,0.1,ihcasym,cf);
	     
		//c2vihctmp = -NLogarithm(c2filterouttmp*fabs(c2filterouttmp)*cf/10*cf/2e3,0.2,1.0,cf); /* C2 transduction output */

        //ihcouttmp[n] = IhcLowPass(c1vihctmp+c2vihctmp,tdres,3000,n,1.0,7);
   //};  /* End of the loop */
   
    ///* Stretched out the IHC output according to nrep (number of repetitions) */
   
    //for(i=0;i<totalstim*nrep;i++)
	//{
		//ihcouttmp[i] = ihcouttmp[(int) (fmod(i,totalstim))];
  	//};   
   	///* Adjust total path delay to IHC output signal */
	//delay      = delay_cat(cf);
	//delaypoint =__max(0,(int) ceil(delay/tdres));    
         
    //for(i=delaypoint;i<totalstim*nrep;i++)
	//{        
		//ihcout[i] = ihcouttmp[i - delaypoint];
  	//};   

    ///* Freeing dynamic memory allocated earlier */

    //free(ihcouttmp);
    //free(mey1); free(mey2); free(mey3);	
    //free(tmpgain);
	//return 0;
//} /* End of the SingleAN function */


/* RTH: the core function for ZilanyBruce 2006/2007 inner hear cell and auditory nerve  
        in this version function returns int value: 0 if it finishes normal or Error Code.
*/
int IHCAN(double *px, double cf, int nrep, double tdres, int totalstim,
                double cohc, double cihc, double *ihcout)
{	
    
    /*variables for middle-ear model */
	double megainmax=43;
    double mey1[3], mey2[3], mey3[3], meout,c1filterouttmp,c2filterouttmp,c1vihctmp,c2vihctmp;
    double fp,C,m11,m12,m21,m22,m23,m24,m25,m26,m31,m32,m33,m34,m35,m36;
	
	/*variables for the signal-path, control-path and onward */
	double *ihcouttmp,*tmpgain;
	int    grd;

    double bmplace,centerfreq,gain,taubm,ratiowb,bmTaubm,fcohc,TauWBMax,TauWBMin,tauwb;
//    double Taumin[1],Taumax[1],bmTaumin[1],bmTaumax[1],ratiobm[1],lasttmpgain,wbgain,ohcasym,ihcasym,delay;
    double Taumin,Taumax,bmTaumin,bmTaumax,ratiobm,lasttmpgain,wbgain,ohcasym,ihcasym,delay;
//	int    i,n,delaypoint,grdelay[1],bmorder,wborder;
	int    i,n,delaypoint,grdelay,bmorder,wborder;
	double wbout1,wbout,ohcnonlinout,ohcout,tmptauc1,tauc1,rsigma,wb_gain;
            
    
    /* Allocate dynamic memory for the temporary variables */
	if ( (ihcouttmp  = (double*)calloc(totalstim*nrep,sizeof(double)) ) == NULL ) return 1;
	    
	if ( (tmpgain = (double*)calloc(totalstim,sizeof(double)) ) == NULL ) return 1;
    
	/** Calculate the location on basilar membrane from CF */	
    
	bmplace = 11.9 * log10(0.80 + cf / 456.0); 
    
	/** Calculate the center frequency for the control-path wideband filter
	    from the location on basilar membrane */
	
	centerfreq = 456.0*(pow(10,(bmplace+1.2)/11.9)-0.80); /* shift the center freq */
    
	/*==================================================================*/
	/*====== Parameters for the gain ===========*/
	gain = 52/2*(tanh(2.2*log10(cf/0.6e3)+0.15)+1);
	/*gain = 52/2*(tanh(2.2*log10(cf/1e3)+0.15)+1);*/
	if(gain>60) gain = 60;  
	if(gain<15) gain = 15;
	/*====== Parameters for the control-path wideband filter =======*/
	bmorder = 3;
	Get_tauwb(cf,bmorder,&Taumax,&Taumin);
	taubm   = cohc*(Taumax-Taumin)+Taumin;
	ratiowb = Taumin/Taumax;
	/*====== Parameters for the signal-path C1 filter ======*/
	Get_taubm(cf,Taumax,&bmTaumax,&bmTaumin,&ratiobm);
	bmTaubm  = cohc*(bmTaumax-bmTaumin)+bmTaumin;
	fcohc    = bmTaumax/bmTaubm;
	/*====== Parameters for the control-path wideband filter =======*/
	wborder  = 3;
	TauWBMax = Taumin+0.2*(Taumax-Taumin);
	TauWBMin = TauWBMax/Taumax*Taumin;
	tauwb    = TauWBMax+(bmTaubm-bmTaumax)*(TauWBMax-TauWBMin)/(bmTaumax-bmTaumin);

	wbgain = gain_groupdelay(tdres,centerfreq,cf,tauwb,&grdelay);
	tmpgain[0]   = wbgain; 
	lasttmpgain  = wbgain;
	/*===============================================================*/
	/* Nonlinear asymmetry of OHC function and IHC C1 transduction function*/
	ohcasym  = 7.0;    
	ihcasym  = 3.0;
	/*===============================================================*/
	/*===============================================================*/
	/* Prewarping and related constants for the middle ear */
	fp = 1e3;  /* prewarping frequency 1 kHz */
	C  = TWOPI*fp/tan(TWOPI/2*fp*tdres);
	m11 = C/(C + 693.48);                    m12 = (693.48 - C)/C;
	m21 = 1/(pow(C,2) + 11053*C + 1.163e8);  m22 = -2*pow(C,2) + 2.326e8;    m23 = pow(C,2) - 11053*C + 1.163e8; 
	m24 = pow(C,2) + 1356.3*C + 7.4417e8;    m25 = -2*pow(C,2) + 14.8834e8;  m26 = pow(C,2) - 1356.3*C + 7.4417e8;
	m31 = 1/(pow(C,2) + 4620*C + 909059944); m32 = -2*pow(C,2) + 2*909059944; m33 = pow(C,2) - 4620*C + 909059944;
	m34 = 5.7585e5*C + 7.1665e7;             m35 = 14.333e7;                 m36 = 7.1665e7 - 5.7585e5*C;

	double *dscan = px, *ddscan = px -1;
	int n0=0, n1=0, n2=0;
	for (n=0; n<totalstim;
			++n,n0=n%3, n1=(n0+2)%3, n2=(n0+1)%3,++dscan,++ddscan) /* Start of the loop */
	{    
		/* Start of the middle-ear filtering section  */
		switch(n){  
			case 0: {
				mey1[n0]  = m11* (*dscan);
				mey2[n0]  = mey1[n0]*m24*m21;
				mey3[n0]  = mey2[n0]*m34*m31;
				meout = mey3[n0]/megainmax ;
				break;
			}
			case 1: {
				mey1[n0]  = m11*(-m12*mey1[n1] + (*dscan)    - (*ddscan));
				mey2[n0]  = m21*(-m22*mey2[n1] + m24*mey1[n0] + m25*mey1[n1]);
				mey3[n0]  = m31*(-m32*mey3[n1] + m34*mey2[n0] + m35*mey2[n1]);
				meout = mey3[n0]/megainmax;
				break;
			}
			default:{
				mey1[n0]  = m11*(-m12*mey1[n1] + (*dscan)    - (*ddscan));
				mey2[n0]  = m21*(-m22*mey2[n1] - m23*mey2[n2] + m24*mey1[n0] + m25*mey1[n1] + m26*mey1[n2]);
				mey3[n0]  = m31*(-m32*mey3[n1] - m33*mey3[n2] + m34*mey2[n0] + m35*mey2[n1] + m36*mey2[n2]);
				meout = mey3[n0]/megainmax;
				break;
			}
		}
		/* End of the middle-ear filtering section */   
     
		/* Control-path filter */
		wbout1 = WbGammaTone(meout,tdres,centerfreq,n,tauwb,wbgain,wborder);
		wbout  = pow((tauwb/TauWBMax),wborder)*wbout1*10e3*__max(1,cf/5e3);

		ohcnonlinout = Boltzman(wbout,ohcasym,12.0,5.0,5.0); /* pass the control signal through OHC Nonlinear Function */
		ohcout = OhcLowPass(ohcnonlinout,tdres,600,n,1.0,2);/* lowpass filtering after the OHC nonlinearity */
        
		tmptauc1 = NLafterohc(ohcout,bmTaumin,bmTaumax,ohcasym); /* nonlinear function after OHC low-pass filter */
		tauc1    = cohc*(tmptauc1-bmTaumin)+bmTaumin;  /* time -constant for the signal-path C1 filter */
		rsigma   = 1/tauc1-1/bmTaumax; /* shift of the location of poles of the C1 filter from the initial positions */

		if (1/tauc1<0.0){
			PyErr_Format(PyExc_ReferenceError,"The poles are in the right-half plane; system is unstable.\n");
			return 2;
		}

		tauwb = TauWBMax+(tauc1-bmTaumax)*(TauWBMax-TauWBMin)/(bmTaumax-bmTaumin);

	    wb_gain = gain_groupdelay(tdres,centerfreq,cf,tauwb,&grdelay);
		
		grd = grdelay; 

		if ((grd+n)<totalstim)
			tmpgain[grd+n] = wb_gain;

		if (tmpgain[n] == 0)
			tmpgain[n] = lasttmpgain;	
		
		wbgain      = tmpgain[n];
		lasttmpgain = wbgain;

        /*====== Signal-path C1 filter ======*/
		 c1filterouttmp = C1ChirpFilt(meout, tdres, cf, n, bmTaumax, rsigma); /* C1 filter output */

        /*====== Parallel-path C2 filter ======*/
		 c2filterouttmp  = C2ChirpFilt(meout, tdres, cf, n, bmTaumax, 1./ratiobm); /* parallel-filter output*/

		/*=== Run the inner hair cell (IHC) section: NL function and then lowpass filtering ===*/
		c1vihctmp  = NLogarithm(cihc*c1filterouttmp,0.1,ihcasym,cf);
		c2vihctmp = -NLogarithm(c2filterouttmp*fabs(c2filterouttmp)*cf/10*cf/2e3,0.2,1.0,cf); /* C2 transduction output */

		ihcouttmp[n] = IhcLowPass(c1vihctmp+c2vihctmp,tdres,3000,n,1.0,7);
	};  /* End of the loop */

	/* Stretched out the IHC output according to nrep (number of repetitions) */
   
	for(i=0;i<totalstim*nrep;i++) {
		ihcouttmp[i] = ihcouttmp[(int) (fmod(i,totalstim))];
	};   

	/* Adjust total path delay to IHC output signal */
	delay      = delay_cat(cf);
	delaypoint =__max(0,(int) ceil(delay/tdres));    

	for(i=delaypoint;i<totalstim*nrep;i++){        
		ihcout[i] = ihcouttmp[i - delaypoint];
	};   

	/* Freeing dynamic memory allocated earlier */
	free(ihcouttmp);
	free(tmpgain);
	return 0;

} /* End of the SingleAN function */


/* -------------------------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------------------------- */
double Get_tauwb(double cf,int order, double *taumax,double *taumin)
{
  double Q10,bw,gain,ratio;
    
  gain = 52/2*(tanh(2.2*log10(cf/0.6e3)+0.15)+1);
  /*gain = 52/2*(tanh(2.2*log10(cf/1e3)+0.15)+1);*/

  if(gain>60) gain = 60;  
  if(gain<15) gain = 15;
   
   ratio = pow(10,(-gain/(20.0*order)));       /* ratio of TauMin/TauMax according to the gain, order */
  
   /*Q10 = pow(10,0.4708*log10(cf/1e3)+0.5469);  /* 75th percentile */
    Q10 = pow(10,0.4708*log10(cf/1e3)+0.4664); /* 50th percentile */
   /*Q10 = pow(10,0.4708*log10(cf/1e3)+0.3934);  /* 25th percentile */
  
  bw     = cf/Q10;
  taumax[0] = 2.0/(TWOPI*bw);
   
  taumin[0]   = taumax[0]*ratio;
  
  return 0;
}
/* -------------------------------------------------------------------------------------------- */
double Get_taubm(double cf, double taumax,double *bmTaumax,double *bmTaumin, double *ratio)
{
  double gain,factor,bwfactor;
    
  gain = 52/2*(tanh(2.2*log10(cf/0.6e3)+0.15)+1);
  /*gain = 52/2*(tanh(2.2*log10(cf/1e3)+0.15)+1);*/
 
  if(gain>60) gain = 60;  
  if(gain<15) gain = 15;

  bwfactor = 0.7;
  factor   = 2.5;

  ratio[0]  = pow(10,(-gain/(20.0*factor))); 

  bmTaumax[0] = taumax/bwfactor;
  bmTaumin[0] = bmTaumax[0]*ratio[0];     
  return 0;
}
/* -------------------------------------------------------------------------------------------- */
/** Pass the signal through the signal-path C1 Tenth Order Nonlinear Chirp-Gammatone Filter */

double C1ChirpFilt(double x, double tdres,double cf, int n, double taumax, double rsigma)
{
    static double C1gain_norm, C1initphase; 
    static double C1input[12][4], C1output[12][4];

    double ipw, ipb, rpa, pzero, rzero;
	double sigma0,fs_bilinear,CF,norm_gain,phase,c1filterout;
	int i,r,order_of_pole,half_order_pole,order_of_zero;
	double temp, dy, preal, pimg;

	COMPLEX p[11]; 
	
	/* Defining initial locations of the poles and zeros */
	/*======== setup the locations of poles and zeros =======*/
	  sigma0 = 1/taumax;
	  ipw    = 1.01*cf*TWOPI-50;
	  ipb    = 0.2343*TWOPI*cf-1104;
	  rpa    = pow(10, log10(cf)*0.9 + 0.55)+ 2000;
	  pzero  = pow(10,log10(cf)*0.7+1.6)+500;

	/*===============================================================*/     
         
     order_of_pole    = 10;             
     half_order_pole  = order_of_pole/2;
     order_of_zero    = half_order_pole;

	 fs_bilinear = TWOPI*cf/tan(TWOPI*cf*tdres/2);
     rzero       = -pzero;
	 CF          = TWOPI*cf;
   
   if (n==0)
   {		  
	p[1].x = -sigma0;     

    p[1].y = ipw;

	p[5].x = p[1].x - rpa; p[5].y = p[1].y - ipb;

    p[3].x = (p[1].x + p[5].x) * 0.5; p[3].y = (p[1].y + p[5].y) * 0.5;

    p[2]   = compconj(p[1]);    p[4] = compconj(p[3]); p[6] = compconj(p[5]);

    p[7]   = p[1]; p[8] = p[2]; p[9] = p[5]; p[10]= p[6];

	   C1initphase = 0.0;
       for (i=1;i<=half_order_pole;i++)          
	   {
           preal     = p[i*2-1].x;
		   pimg      = p[i*2-1].y;
	       C1initphase = C1initphase + atan(CF/(-rzero))-atan((CF-pimg)/(-preal))-atan((CF+pimg)/(-preal));
	   };

	/*===================== Initialize C1input & C1output =====================*/

      for (i=1;i<=(half_order_pole+1);i++)          
      {
		   C1input[i][3] = 0; 
		   C1input[i][2] = 0; 
		   C1input[i][1] = 0;
		   C1output[i][3] = 0; 
		   C1output[i][2] = 0; 
		   C1output[i][1] = 0;
      }

	/*===================== normalize the gain =====================*/
    
      C1gain_norm = 1.0;
      for (r=1; r<=order_of_pole; r++)
		   C1gain_norm = C1gain_norm*(pow((CF - p[r].y),2) + p[r].x*p[r].x);
      
   };
     
    norm_gain= sqrt(C1gain_norm)/pow(sqrt(CF*CF+rzero*rzero),order_of_zero);
	
	p[1].x = -sigma0 - rsigma;

	if (p[1].x>0.0) fprintf(stderr,"The system becomes unstable.\n");
	
	p[1].y = ipw;

	p[5].x = p[1].x - rpa; p[5].y = p[1].y - ipb;

    p[3].x = (p[1].x + p[5].x) * 0.5; p[3].y = (p[1].y + p[5].y) * 0.5;

    p[2] = compconj(p[1]); p[4] = compconj(p[3]); p[6] = compconj(p[5]);

    p[7] = p[1]; p[8] = p[2]; p[9] = p[5]; p[10]= p[6];

    phase = 0.0;
    for (i=1;i<=half_order_pole;i++)          
    {
           preal = p[i*2-1].x;
		   pimg  = p[i*2-1].y;
	       phase = phase-atan((CF-pimg)/(-preal))-atan((CF+pimg)/(-preal));
	};

	rzero = -CF/tan((C1initphase-phase)/order_of_zero);

    if (rzero>0.0) fprintf(stderr,"The zeros are in the right-half plane.\n");
	 
   /*%==================================================  */
	/*each loop below is for a pair of poles and one zero */
   /*%      time loop begins here                         */
   /*%==================================================  */
 
       C1input[1][3]=C1input[1][2]; 
	   C1input[1][2]=C1input[1][1]; 
	   C1input[1][1]= x;

       for (i=1;i<=half_order_pole;i++)          
       {
           preal = p[i*2-1].x;
		   pimg  = p[i*2-1].y;
		  	   
           temp  = pow((fs_bilinear-preal),2)+ pow(pimg,2);
		   

           /*dy = (input[i][1] + (1-(fs_bilinear+rzero)/(fs_bilinear-rzero))*input[i][2]
                                 - (fs_bilinear+rzero)/(fs_bilinear-rzero)*input[i][3] );
           dy = dy+2*output[i][1]*(fs_bilinear*fs_bilinear-preal*preal-pimg*pimg);

           dy = dy-output[i][2]*((fs_bilinear+preal)*(fs_bilinear+preal)+pimg*pimg);*/
		   
	       dy = C1input[i][1]*(fs_bilinear-rzero) - 2*rzero*C1input[i][2] - (fs_bilinear+rzero)*C1input[i][3]
                 +2*C1output[i][1]*(fs_bilinear*fs_bilinear-preal*preal-pimg*pimg)
			     -C1output[i][2]*((fs_bilinear+preal)*(fs_bilinear+preal)+pimg*pimg);

		   dy = dy/temp;

		   C1input[i+1][3] = C1output[i][2]; 
		   C1input[i+1][2] = C1output[i][1]; 
		   C1input[i+1][1] = dy;

		   C1output[i][2] = C1output[i][1]; 
		   C1output[i][1] = dy;
       }

	   dy = C1output[half_order_pole][1]*norm_gain;  /* don't forget the gain term */
	   c1filterout= dy/4.0;   /* signal path output is divided by 4 to give correct C1 filter gain */
	                   
     return (c1filterout);
}  

/* -------------------------------------------------------------------------------------------- */
/** Parallelpath C2 filter: same as the signal-path C1 filter with the OHC completely impaired */

double C2ChirpFilt(double xx, double tdres,double cf, int n, double taumax, double fcohc)
{
	static double C2gain_norm, C2initphase;
    static double C2input[12][4];  static double C2output[12][4];
   
	double ipw, ipb, rpa, pzero, rzero;

	double sigma0,fs_bilinear,CF,norm_gain,phase,c2filterout;
	int    i,r,order_of_pole,half_order_pole,order_of_zero;
	double temp, dy, preal, pimg;

	COMPLEX p[11]; 	
    
    /*================ setup the locations of poles and zeros =======*/

	  sigma0 = 1/taumax;
	  ipw    = 1.01*cf*TWOPI-50;
      ipb    = 0.2343*TWOPI*cf-1104;
	  rpa    = pow(10, log10(cf)*0.9 + 0.55)+ 2000;
	  pzero  = pow(10,log10(cf)*0.7+1.6)+500;
	/*===============================================================*/     
         
     order_of_pole    = 10;             
     half_order_pole  = order_of_pole/2;
     order_of_zero    = half_order_pole;

	 fs_bilinear = TWOPI*cf/tan(TWOPI*cf*tdres/2);
     rzero       = -pzero;
	 CF          = TWOPI*cf;
   	    
    if (n==0)
    {		  
	p[1].x = -sigma0;     

    p[1].y = ipw;

	p[5].x = p[1].x - rpa; p[5].y = p[1].y - ipb;

    p[3].x = (p[1].x + p[5].x) * 0.5; p[3].y = (p[1].y + p[5].y) * 0.5;

    p[2] = compconj(p[1]); p[4] = compconj(p[3]); p[6] = compconj(p[5]);

    p[7] = p[1]; p[8] = p[2]; p[9] = p[5]; p[10]= p[6];

	   C2initphase = 0.0;
       for (i=1;i<=half_order_pole;i++)         
	   {
           preal     = p[i*2-1].x;
		   pimg      = p[i*2-1].y;
	       C2initphase = C2initphase + atan(CF/(-rzero))-atan((CF-pimg)/(-preal))-atan((CF+pimg)/(-preal));
	   };

	/*===================== Initialize C2input & C2output =====================*/

      for (i=1;i<=(half_order_pole+1);i++)          
      {
		   C2input[i][3] = 0; 
		   C2input[i][2] = 0; 
		   C2input[i][1] = 0;
		   C2output[i][3] = 0; 
		   C2output[i][2] = 0; 
		   C2output[i][1] = 0;
      }
    
    /*===================== normalize the gain =====================*/
    
     C2gain_norm = 1.0;
     for (r=1; r<=order_of_pole; r++)
		   C2gain_norm = C2gain_norm*(pow((CF - p[r].y),2) + p[r].x*p[r].x);
    };
     
    norm_gain= sqrt(C2gain_norm)/pow(sqrt(CF*CF+rzero*rzero),order_of_zero);
    
	p[1].x = -sigma0*fcohc;

	if (p[1].x>0.0) fprintf(stderr,"The system becomes unstable.\n");
	
	p[1].y = ipw;

	p[5].x = p[1].x - rpa; p[5].y = p[1].y - ipb;

    p[3].x = (p[1].x + p[5].x) * 0.5; p[3].y = (p[1].y + p[5].y) * 0.5;

    p[2] = compconj(p[1]); p[4] = compconj(p[3]); p[6] = compconj(p[5]);

    p[7] = p[1]; p[8] = p[2]; p[9] = p[5]; p[10]= p[6];

    phase = 0.0;
    for (i=1;i<=half_order_pole;i++)          
    {
           preal = p[i*2-1].x;
		   pimg  = p[i*2-1].y;
	       phase = phase-atan((CF-pimg)/(-preal))-atan((CF+pimg)/(-preal));
	};

	rzero = -CF/tan((C2initphase-phase)/order_of_zero);	
    if (rzero>0.0) fprintf(stderr,"The zeros are in the right-hand plane.\n");
   /*%==================================================  */
   /*%      time loop begins here                         */
   /*%==================================================  */

       C2input[1][3]=C2input[1][2]; 
	   C2input[1][2]=C2input[1][1]; 
	   C2input[1][1]= xx;

      for (i=1;i<=half_order_pole;i++)          
      {
           preal = p[i*2-1].x;
		   pimg  = p[i*2-1].y;
		  	   
           temp  = pow((fs_bilinear-preal),2)+ pow(pimg,2);
		   
           /*dy = (input[i][1] + (1-(fs_bilinear+rzero)/(fs_bilinear-rzero))*input[i][2]
                                 - (fs_bilinear+rzero)/(fs_bilinear-rzero)*input[i][3] );
           dy = dy+2*output[i][1]*(fs_bilinear*fs_bilinear-preal*preal-pimg*pimg);

           dy = dy-output[i][2]*((fs_bilinear+preal)*(fs_bilinear+preal)+pimg*pimg);*/
		   
	      dy = C2input[i][1]*(fs_bilinear-rzero) - 2*rzero*C2input[i][2] - (fs_bilinear+rzero)*C2input[i][3]
                 +2*C2output[i][1]*(fs_bilinear*fs_bilinear-preal*preal-pimg*pimg)
			     -C2output[i][2]*((fs_bilinear+preal)*(fs_bilinear+preal)+pimg*pimg);

		   dy = dy/temp;

		   C2input[i+1][3] = C2output[i][2]; 
		   C2input[i+1][2] = C2output[i][1]; 
		   C2input[i+1][1] = dy;

		   C2output[i][2] = C2output[i][1]; 
		   C2output[i][1] = dy;

       };

	  dy = C2output[half_order_pole][1]*norm_gain;
	  c2filterout= dy/4.0;
	  
	  return (c2filterout); 
}   

/* -------------------------------------------------------------------------------------------- */
/** Pass the signal through the Control path Third Order Nonlinear Gammatone Filter */

double WbGammaTone(double x,double tdres,double centerfreq, int n, double tau,double gain,int order)
{
  static double wbphase;
  static COMPLEX wbgtf[4], wbgtfl[4];

  double delta_phase,dtmp,c1LP,c2LP,out;
  int i,j;
  
  if (n==0)
  {
      wbphase = 0;
      for(i=0; i<=order;i++)
      {
            wbgtfl[i] = compmult(0,compexp(0));
            wbgtf[i]  = compmult(0,compexp(0));
      }
  }
  
  delta_phase = -TWOPI*centerfreq*tdres;
  wbphase += delta_phase;
  
  dtmp = tau*2.0/tdres;
  c1LP = (dtmp-1)/(dtmp+1);
  c2LP = 1.0/(dtmp+1);
  wbgtf[0] = compmult(x,compexp(wbphase));                 /* FREQUENCY SHIFT */
  
  for(j = 1; j <= order; j++)                              /* IIR Bilinear transformation LPF */
  wbgtf[j] = comp2sum(compmult(c2LP*gain,comp2sum(wbgtf[j-1],wbgtfl[j-1])),
      compmult(c1LP,wbgtfl[j]));
  out = REAL(compprod(compexp(-wbphase), wbgtf[order])); /* FREQ SHIFT BACK UP */
  
  for(i=0; i<=order;i++) wbgtfl[i] = wbgtf[i];
  return(out);
}

/* -------------------------------------------------------------------------------------------- */
/** Calculate the gain and group delay for the Control path Filter */

double gain_groupdelay(double tdres,double centerfreq, double cf, double tau,int *grdelay)
{ 
  double tmpcos,dtmp2,c1LP,c2LP,tmp1,tmp2,wb_gain;

  tmpcos = cos(TWOPI*(centerfreq-cf)*tdres);
  dtmp2 = tau*2.0/tdres;
  c1LP = (dtmp2-1)/(dtmp2+1);
  c2LP = 1.0/(dtmp2+1);
  tmp1 = 1+c1LP*c1LP-2*c1LP*tmpcos;
  tmp2 = 2*c2LP*c2LP*(1+tmpcos);
  
  wb_gain = pow(tmp1/tmp2, 1.0/2.0);
  
  grdelay[0] = (int)floor((0.5-(c1LP*c1LP-c1LP*tmpcos)/(1+c1LP*c1LP-2*c1LP*tmpcos)));

  return(wb_gain);
}
/* -------------------------------------------------------------------------------------------- */
/** Calculate the delay (basilar membrane, synapse, etc. for cat) */

double delay_cat(double cf)
{  
  double A0,A1,x,delay;

  A0    = 3.0;  
  A1    = 12.5;
  x     = 11.9 * log10(0.80 + cf / 456.0);      /* cat mapping */
  delay = A0 * exp( -x/A1 ) * 1e-3;
  
  return(delay);
}
/* -------------------------------------------------------------------------------------------- */
/* Get the output of the OHC Nonlinear Function (Boltzman Function) */

double Boltzman(double x, double asym, double s0, double s1, double x1)
  {
	double shift,x0,out1,out;

    shift = 1.0/(1.0+asym);  /* asym is the ratio of positive Max to negative Max*/
    x0    = s0*log((1.0/shift-1)/(1+exp(x1/s1)));
	    
    out1 = 1.0/(1.0+exp(-(x-x0)/s0)*(1.0+exp(-(x-x1)/s1)))-shift;
	out = out1/(1-shift);

    return(out);
  }  /* output of the nonlinear function, the output is normalized with maximum value of 1 */
  
/* -------------------------------------------------------------------------------------------- */
/* Get the output of the OHC Low Pass Filter in the Control path */

double OhcLowPass(double x,double tdres,double Fc, int n,double gain,int order)
{
  static double ohc[4],ohcl[4];

  double c,c1LP,c2LP;
  int i,j;

  if (n==0)
  {
      for(i=0; i<(order+1);i++)
      {
          ohc[i] = 0;
          ohcl[i] = 0;
      }
  }    
  
  c = 2.0/tdres;
  c1LP = ( c - TWOPI*Fc ) / ( c + TWOPI*Fc );
  c2LP = TWOPI*Fc / (TWOPI*Fc + c);
  
  ohc[0] = x*gain;
  for(i=0; i<order;i++)
    ohc[i+1] = c1LP*ohcl[i+1] + c2LP*(ohc[i]+ohcl[i]);
  for(j=0; j<=order;j++) ohcl[j] = ohc[j];
  return(ohc[order]);
}
/* -------------------------------------------------------------------------------------------- */
/* Get the output of the IHC Low Pass Filter  */

double IhcLowPass(double x,double tdres,double Fc, int n,double gain,int order)
{
  static double ihc[8],ihcl[8];
  
  double C,c1LP,c2LP;
  int i,j;

  if (n==0)
  {
      for(i=0; i<(order+1);i++)
      {
          ihc[i] = 0;
          ihcl[i] = 0;
      }
  }     
  
  C = 2.0/tdres;
  c1LP = ( C - TWOPI*Fc ) / ( C + TWOPI*Fc );
  c2LP = TWOPI*Fc / (TWOPI*Fc + C);
  
  ihc[0] = x*gain;
  for(i=0; i<order;i++)
    ihc[i+1] = c1LP*ihcl[i+1] + c2LP*(ihc[i]+ihcl[i]);
  for(j=0; j<=order;j++) ihcl[j] = ihc[j];
  return(ihc[order]);
}
/* -------------------------------------------------------------------------------------------- */
/* Get the output of the Control path using Nonlinear Function after OHC */

double NLafterohc(double x,double taumin, double taumax, double asym)
{    
	double R,dc,R1,s0,x1,out,minR;

	minR = 0.05;
    R  = taumin/taumax;
    
	if(R<minR) minR = 0.5*R;
    else       minR = minR;
    
    dc = (asym-1)/(asym+1.0)/2.0-minR;
    R1 = R-minR;

    /* This is for new nonlinearity */
    s0 = -dc/log(R1/(1-minR));
	
    x1  = fabs(x);
    out = taumax*(minR+(1.0-minR)*exp(-x1/s0));
	if (out<taumin) out = taumin; 
    if (out>taumax) out = taumax;
    return(out);
}
/* -------------------------------------------------------------------------------------------- */
/* Get the output of the IHC Nonlinear Function (Logarithmic Transduction Functions) */

double NLogarithm(double x, double slope, double asym, double cf)
{
	double corner,strength,xx,splx,asym_t;
	    
    corner    = 80; 
    strength  = 20.0e6/pow(10,corner/20);
            
    xx = log(1.0+strength*fabs(x))*slope;
    
    if(x<0)
	{
		splx   = 20*log10(-x/20e-6);
		asym_t = asym -(asym-1)/(1+exp(splx/5.0));
		xx = -1/asym_t*xx;
	};   
    return(xx);
}
/* -------------------------------------------------------------------------------------------- */
