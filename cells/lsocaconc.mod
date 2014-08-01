TITLE ca_conc.mod adapted from Ms Thesis of C.M. Gruner

UNITS {
	(molar) = (1/liter)
	(mV) = (millivolt)
	(mA) = (milliamp)
	(mM) = (millimolar)
	FARADAY = (faraday) (coulomb)
	R = (k-mole)	(joule/degC)
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
		SUFFIX lsocaconc
		USEION ca READ ica, cao, cai WRITE cai, eca
:		RANGE
		::: RTH>
		RANGE depth, Pumptau
		::: <RTH
}

PARAMETER {
		celsius (degC)
		equicaconc = 5e-5 (mM)
		basecaconc = 5e-5 (mM)
		c = 5.2e-3 (mM-cm3/millicoulomb)
		depth = 3.15e-6 (cm)
		Pumptau = 4 (ms)
		ica (mA/cm2)
		cao = 4 (mM)
}

ASSIGNED {
		eca (mV)
}

STATE {
		cai (mM)
}

BREAKPOINT {
	SOLVE ca_conc METHOD cnexp
	eca = (1000)*R*(celsius + 273.15)/(2*FARADAY) * log(cao/cai)
}

INITIAL {
	cai = basecaconc
	eca = 141.12
}

DERIVATIVE ca_conc {  
	cai' = -(.001) * (c/depth*ica) - (cai - equicaconc)/Pumptau
}
