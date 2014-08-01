TITLE lso_axon.mod adapted from Ms Thesis of C.M. Gruner

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

NEURON {
		SUFFIX lsoaxon
		USEION na READ ena WRITE ina
		USEION k READ ek WRITE ik
		NONSPECIFIC_CURRENT il
		RANGE gnabar, gkbar, gl, el
		::: RTH>
		:GLOBAL minf, ninf, hinf
		RANGE minf, ninf, hinf
		::: <RTH
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
		v (mV)
		celsius = 36.0 (degC)
		dt (ms)
		gnabar = .17 (mho/cm2)
		ena = 55 (mV)
		gkbar = .02 (mho/cm2)
		ek = -80 (mV)
		gl = .000025 (mho/cm2)
		er = -62.0 (mV)
		Msh = 2.3 (mV)
		Hsh = -10.8 (mV)
		Nsh = 2.6 (mV)
		delta0 = .19
		deltaa = 1.0
		q10 = 16
}

STATE {
		m h n
}

ASSIGNED {
		ina (mA/cm2)
		ik (mA/cm2)
		il (mA/cm2)
		el (mV)
		minf hinf ninf
}

LOCAL mexp, hexp, nexp

BREAKPOINT {
	SOLVE states
	ina = gnabar*m*m*m*h*(v - ena)
	ik = gkbar*n*n*n*n*(v - ek)
	il = gl*(v - el)
}

UNITSOFF

INITIAL {
		rates(v)
		m = minf
		h = hinf
		n = ninf
		el = er + (gnabar*m*m*m*h*(er-ena)+gkbar*n*n*n*n*(er-ek))/gl
}

PROCEDURE states () {
		rates(v)
		m = m + mexp*(minf-m)
		h = h + hexp*(hinf-h)
		n = n + nexp*(ninf-n)
		::: RTH>
		:VERBATIM
		:return 0;
		:ENDVERBATIM
		::: <RTH
}

PROCEDURE rates (v) {

		LOCAL tinc, alpha, beta, sum, delta

		TABLE minf, mexp, hinf, hexp, ninf, nexp
		DEPEND dt, Msh, Hsh, Nsh, delta0, deltaa, q10
		FROM -100 TO 100 WITH 200

		tinc = -dt*q10

: m sodium activation system
		alpha = .1 * vtrap(-(v+37+Msh),10)
		beta = 4 * exp(-(v+62+Msh)/18)
		sum = alpha + beta
		minf = alpha/sum
		mexp = 1 - exp(tinc*sum)

: h sodium activation system
		alpha = .07 * exp(-(v+62+Hsh)/20)
		beta = 1 / (exp(-(v+32+Hsh)/10)+1)
		sum = alpha + beta
		hinf = alpha/sum
		hexp = 1 - exp(tinc*sum)

: n potassium activation system
		alpha = .01 * vtrap(-(v+52+Nsh),10)
		beta = .125*exp(-(v+62+Nsh)/80)
		sum = alpha + beta
		ninf = alpha/sum
		delta = deltaa * (delta0 + .0087*(1-delta0)*(v-er))
		nexp = 1 - exp(tinc*sum*delta)
}

FUNCTION vtrap(x,y) {
		if (fabs(x/y) < 1e-6) {
				vtrap = y*(1-x/y/2)
		} else{
				vtrap = x/(exp(x/y)-1)
		}
}

UNITSON
