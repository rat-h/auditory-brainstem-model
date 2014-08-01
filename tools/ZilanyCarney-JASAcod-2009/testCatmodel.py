import numpy as np
import scipy as sp
from  scipy.io import loadmat

import matplotlib.pyplot as plt
#from ffGn import ffGn
import ZilanyCarney2009AN as an

CF    = 10.0e3 # CF in Hz; 
cohc  = 1.0 #  normal ohc function
cihc  = 1.0 #  normal ihc function
fiberType = 3 #  spontaneous rate (in spikes/s) of the fiber BEFORE refractory effects; "1" = Low; "2" = Medium; "3" = High
implnt = 0 #  "0" for approximate or "1" for actual implementation of the power-law functions in the Synapse
# stimulus parameters
F0 = CF #  stimulus frequency in Hz
Fs = 100e3 #  sampling rate in Hz (must be 100, 200 or 500 kHz)
T  = 50e-3 #  stimulus duration in seconds
rt = 5e-3 #  rise/fall time in seconds
stimdb = 10 #  stimulus intensity in dB SPL
# PSTH parameters
nrep = 1              # number of stimulus repetitions (e.g., 50);
psthbinwidth = 0.5e-3 #  binwidth in seconds;

t = np.arange(0,T-1/Fs,1/Fs) #  time vector
mxpts = t.size
irpts = rt*Fs

pin = np.sqrt(2)*20e-6*np.power(10.0,float(stimdb)/20.)*np.sin(2*np.pi*F0*t) #  unramped stimulus
pin[0:irpts-1]=pin[0:irpts-1]*np.arange(0,(irpts-1))/irpts
pin[(mxpts-irpts-1):]=pin[(mxpts-irpts-1):]*np.arange(irpts,-1,-1)/irpts

vihc = an.ihc(pin,CF,nrep,1./Fs,T*2.,cohc,cihc)
print "===vihc [100] = %g ==="%vihc[100]
print "===vihc [500] = %g ==="%vihc[500]
print "   vihc.size  = %d ==="%vihc.size
#delaypoint = int(np.floor(7500/(CF/1e3)))
#arg1 = int(np.ceil(vihc.size+2*delaypoint))
#if fiberType == 3:spont = 100.0
#elif fiberType == 2: spont = 5.0
#else : spont = 0.1
#randVec = ffGn(arg1,1e-4,0.9,spont)
#plt.plot(np.arange(randVec.size),randVec)
#plt.show()

synout,psth = an.synapse(vihc,CF,nrep,1./Fs,fiberType,implnt) 
print "SIZES:",synout.size, vihc.size

timeout = np.arange(0,psth.size)/float(Fs)
#psthbins = np.round(psthbinwidth*Fs) #  number of psth bins per psth bin
#psthtime = timeout[0::psthbins] #  time vector for psth
#pr = np.sum(np.reshape(psth,psthbins,psth.size/psthbins))/nrep #  pr of spike in each bin
#Psth = pr/psthbinwidth #  psth in units of spikes/s
origdata = loadmat("testCatmodel.mat")

plt.figure(1)
plt.subplot(4,1,1)
plt.plot(timeout,np.hstack((pin,np.zeros(timeout.size-pin.size))) )
plt.title('Input Stimulus')

plt.subplot(4,1,2)
plt.plot(timeout,vihc[0:timeout.size],"k-",lw=2)
plt.plot(timeout,origdata["vihc"][0],"r--",lw=2)
plt.title('IHC output')

plt.subplot(4,1,3)
plt.plot(timeout,synout,"k-",lw=2) 
plt.plot(timeout,origdata["synout"][0],"r--",lw=2)
plt.title('Synapse Output')
#xlabel('Time (s)')
#####!!!!!!
#plt.subplot(4,1,4)
#plt.plot(psthtime,Psth)
#plt.title('psth')
#plt.xlabel('Time (s)')
plt.subplot(4,1,4)
plt.plot(timeout,psth,"k-",lw=2)
plt.plot(timeout,origdata["psth"][0],"r--",lw=2)
plt.title('psth')
#plt.xlabel('Time (s)')

plt.show()
