TITLE tca.mod adapted from MS Thesis of C.M. Gruner

UNITS {
	(molar) = (1/liter)
	(mV) = (millivolt)
	(mA) = (milliamp)
	(mM) = (millimolar)
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
		SUFFIX lsotca
		USEION ca READ eca, cai WRITE ica
		NONSPECIFIC_CURRENT ikca
		:USEION kca READ ekca WRITE ikca
		:RANGE ekca
		RANGE gcabar, gahpbar
		::: RTH >
		:GLOBAL sinf, stau, rinf, rtau, qinf, qtau
		RANGE sinf, stau, rinf, rtau, qinf, qtau
		RANGE Qa0, Qah, Qsl, Qb0
		::: < RTH
}

PARAMETER {
		celsius (degC)
		v (mV)
		dt (ms)
		gcabar = .125 (mho/cm2)
		Sa0 = .1 (1/ms-1/mV)
		Sb0 = .00375 (1/ms-1/mV)
		Sah = 60 (mV)
		Ssl = 10 (mV)
		Sbh = 45 (mV)
		Ra0 = 1.2 (1/ms)
		Rb0 = 4.68 (1/mM-1/ms)
		Rbh = 1.0 (mM)
		Rsl = .25 (mM)
		gahpbar = 0.022 (mho/cm2)
		Qa0 = 2925 (1/mM-1/ms)
		Qah = 1 (mM)
		Qsl = .2 (mM)
		Qb0 = 300 (1/ms)
		cai (mM)
		eca (mV)
		ekca = -80 (mV)
		vrest = -62.0 (mV)
}

STATE {
		s r q gahp
}

ASSIGNED {
		ica (mA/cm2)
		ikca (mA/cm2)
		sinf stau rinf rtau qinf qtau
}

LOCAL sexp, rexp, qexp

BREAKPOINT {
	SOLVE states : METHOD
	ica = gcabar*s*s*s*s*s*r*(v - eca)
	ikca = gahpbar*q*(v - ekca)
}

UNITSOFF

INITIAL {
		vrates(v)
		crates(cai)
		s = sinf
		r = rinf
		q = qinf
		gahp = gahpbar*q
		ica = gcabar*s*s*s*s*s*r*(v - eca)
		ikca = gahpbar*q*(v - ekca)
}

PROCEDURE states() {
		vrates(v)
		crates(cai)
		s = s + sexp*(sinf - s)
		r = r + rexp*(rinf - r)
		q = q + qexp*(qinf - q)
		gahp = gahpbar*q
		::: RTH>
		:VERBATIM
		:return 0;
		:ENDVERBATIM
		::: <RTH
}

PROCEDURE vrates(v) {
		LOCAL tinc, alpha, beta, sum

		TABLE sinf, sexp, stau
		DEPEND dt, Sa0, Sb0, Sah, Sbh, Ssl

FROM -100 TO 50 WITH 200

		tinc = -dt
:s calcium activation system
		alpha = Sa0 * vtrap((Sah-(v-vrest)),Ssl)
		beta = Sb0 * vtrap((v-vrest-Sbh),Ssl)
		sum = alpha + beta
		stau = 1/(sum)
		sinf = alpha/sum
		sexp = 1 - exp(tinc*sum)
}

PROCEDURE crates(cai) {
		LOCAL tinc, alpha, beta, sum

		TABLE rinf, rexp, rtau, qinf, qexp, qtau
		DEPEND dt, Ra0, Rb0, Rbh, Rsl, Qa0, Qah, Qsl, Qb0

FROM 0 TO 1 WITH 400

		tinc = -dt
:r calcium activation system
		alpha = Ra0
		beta = Rb0 * vtrap((Rbh-cai),Rsl)

		sum = alpha + beta
		rtau = 1/(sum)
		rinf = alpha/sum
		rexp = 1 - exp(tinc*sum)

:q potassium (K) activation system
		alpha = Qa0 * vtrap((Qah-cai),Qsl)
		beta = Qb0

		sum = alpha + beta
		qinf = alpha/sum
		qtau = 1/(sum)
		qexp = 1 - exp(tinc*sum)
}

FUNCTION vtrap(x,y) {
		if (fabs(x/y) < 1e-6) {
				vtrap = y*(1-x/y/2)
		} else{
				vtrap = x/(exp(x/y)-1)
		}
}

UNITSON
