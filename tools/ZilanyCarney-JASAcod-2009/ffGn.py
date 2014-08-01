import numpy as np
import scipy.signal as ss
import matplotlib.pyplot as plt
def ffGn(N, tdres, Hinput, mu=None, sigma=None):
	'''
	FFGN  Fast (exact) fractional Gaussian noise and Brownian motion generator.
	
	Y = FFGN(N, Hinput, MU, SIGMA) returns a vector containing a sequence of fractional Gaussian 
	noise or fractional Brownian motion.  The generation process uses an FFT which makes it 
	very fast.  The input arguments are:

		N			is the length of the output sequence.
		H			is the "Hurst" index of the resultant noise (0 < H <= 2).  For 0 < H <= 1, 
					  the output will be fractional Gaussian noise with Hurst index H.  For 
					  1 < H <= 2, the output will be fractional Brownian motion with Hurst
					  index H-1.  Either way, the power spectral density of the output will
					  be nominally proportional to 1/f^(2H-1).
		mu			is the mean of the noise. [default = 0]
		sigma		is the standard deviation of the noise. [default = 1]

	FFGN(N, H) returns a sequence of fractional Gaussian noise with a mean of zero
	and a standard deviation of one or fractional Brownian motion derived from such
	fractional Gaussian noise.

 	References: Davies & Harte (1987); Beran (1994); Bardet et al., 2002
	This method is based on an embedding of the covariance matrix in a circulant matrix.	

   Copyright (C) 2003-2005 by B. Scott Jackson
   Revision: 1.3	Date: Aug 28, 2008 by M. S. A. Zilany
					Sigma is deifined for diff. sponts (mu) and Resampling has been introduced to be compatible with the AN model 
   Revision: 1.2	Date: March 14, 2005
   History:
	   Rev. 1.2 - 3/14/05 - Added some additional documentation and input argument checking.
	   Rev. 1.1 - 9/15/04 - Added the persistent variables and associated "if"-statement.
	   Rev. 1.0 - 2/11/03 - Original version.
	'''
#---- Check input arguments ---------- #
#	print N, tdres, Hinput, mu, sigma
	if (type(N) is not int) or (type(Hinput) is not float) or (mu != None and type(mu) is not float) or ( sigma != None and type(sigma) is not float):
		print (type(N) is not int), (type(Hinput) is not float), (mu != None and type(mu) is not float),( sigma != None and type(sigma) is not float)
		raise ValueError('All input arguments must be finite real scalars.\n')
	if N <= 0:
		raise ValueError('Length of the return vector must be positive.')

	if tdres > 1:
		raise ValueError('Original sampling rate should be checked.')

	if (Hinput < 0) or (Hinput > 2):
		raise ValueError('The Hurst parameter must be in the interval (0,2].')

	# Downsampling No. of points to match with those of Scott jackson (tau 1e-1)
	resamp = np.ceil(1e-1/tdres)
#	print "resamp=",resamp
	nop = N
	N = np.ceil(N/resamp)+1 
	if N < 10: N = 10;

	# Determine whether fGn or fBn should be produced.
	if  Hinput <= 1 :
		H,fBn = Hinput, False
	else:
		H,fBn = Hinput - 1, True
	
	def initvar(N,H):
		Nfft = 2**np.ceil(np.log2(2*(N-1)))
		NfftHalf = np.around(Nfft/2)
		k = np.hstack( (np.arange(0,NfftHalf), np.arange(NfftHalf-1,-1,-1) ) )
		Zmag = 0.5*( (k+1)**(2.*H) - 2.*k**(2.*H) + (np.abs(k-1))**(2.*H) )
		Zmag = np.real(np.fft.fft(Zmag))
		if np.any(Zmag < 0) :
			sys.stderr.write('The fast Fourier transform of the circulant covariance had negative values.');
			sys.exit(1)
		del k
		return N,H,Nfft,np.sqrt(Zmag)
		
	# Calculate the fGn.
	if H == 0.5:
		y = np.randn(N);  # If H=0.5, then fGn is equivalent to white Gaussian noise.
	else:
		# If this function was already in memory before being called this time,
		# AND the values for N and H are the same as the last time it was
		# called, then the following (persistent) variables do not need to be
		# recalculated.  This was done to improve the speed of this function,
		# especially when many samples of a single fGn (or fBn) process are
		# needed by the calling function.
		if not hasattr(ffGn, "Zmag") or not hasattr(ffGn, "Nfft") or hasattr(ffGn, "Nlast") or hasattr(ffGn, "Hlast"):
			ffGn.Nlast,ffGn.Hlast,ffGn.Nfft,ffGn.Zmag = initvar(N,H)
		elif ffGn.Hlast != H or ffGn.Nlast != N: 
			ffGn.Nlast,ffGn.Hlast,ffGn.Nfft,ffGn.Zmag = initvar(N,H)
		Z = ffGn.Zmag*(np.random.randn(ffGn.Nfft) + 1j* np.random.randn(ffGn.Nfft))
		y = np.real(np.fft.ifft(Z))*np.sqrt(ffGn.Nfft)
		del Z
		y = y[:N]
	
	# Convert the fGn to fBn, if necessary.
	if fBn: y = np.cumsum(y)


	# Resampling back to original (1/tdres): match with the AN model
#	print "\n==\nysize=",y.size,"resamp=",resamp,"N=",N,"\n==\n"
	y = ss.resample(y,resamp*y.size)  # Resampling to match with the AN model
#	plt.subplot(211)
#	plt.plot(y)

	# define standard deviation
	if mu == None:
		mu,sigma = 0.,1.
	elif sigma == None and mu < 0.5:
		sigma = 5
	elif sigma == None and mu < 18:
		sigma = 50				# 7 when added after powerlaw
	elif sigma == None:
		sigma = 200				# 40 when added after powerlaw
	y = y*sigma #+mu?????
	y = y[0:nop]
#	plt.subplot(212)
#	plt.plot(y)
#	plt.show()
	return y


def resample(x, num, t=None, axis=0, window=None):
	return ss.resample(x,num,t,axis,window)

def rand(n):
	return np.random.rand(n)






