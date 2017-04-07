# CELLS section #

CELLS section has two options read by script.

| **Option** | **Option Type** | **Description** |
|:-----------|:----------------|:----------------|
|CellClasses| _string_ or _list of strings_| Each string is a name of imported cell class. Each _cell class_ is an option in CELLS section. It contains a _string_ with import command. Command should import **ONLY** cell class!|
|ModsCopy|_string_ or _list_ of _stings_| Name or names of directories which will be scanned for NEURON mod files. Each mod file will be copy to root directory.|


---


### Life Example ###


```
[CELLS]
CellClasses	= ('AN','VCN','LSO')
AN	:'from spklin import  spklin'
VCN	:'from RaM03  import vcnRaMbase'
LSO	:'from LSO    import LSOcell'
ModsCopy	= @GENERAL:pyextrapath@
```

|[STIMULI section <PREVIOUS](STIMULI.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT> POPULATIONS section](POPULATIONS.md)|
|:--------------------------------------|:----------------------------------------------------------|:-------------------------------------------|
