# SYNAPSES Section #
First, SYNAPSES is not obligatory section. You may skip it. However if you are going to skip it think twice, because model _without_ SYNAPSES section is significantly slower than model with it.

The main concept of SYNAPSES section is shown on this picture.

![https://storage.r-a-r.org/index.php/apps/files_sharing/publicpreview/fSKHgAPyMyZHi87?x=1920&y=629&a=true&file=Synapses_section.jpg&scalingup=0](https://storage.r-a-r.org/index.php/apps/files_sharing/publicpreview/fSKHgAPyMyZHi87?x=1920&y=629&a=true&file=Synapses_section.jpg&scalingup=0)

In general, options in SYNAPSES section allow recognize the same kind of synapse and connect all sources to one object, represented synapse.
If synaptic objects is defined in [CONNECTIONS section](CONNECTIONS.md), a new synaptic object will be added for each source.

Each option in SYSNAPSES is a dictionary with only one obligatory key: **module**. The value of this key is a object which will created. All other keys are parameters of this object.

**Warning!** In SYNAPSES section arbitrary options are not allowed. **Each option in SYNAPSES Section is considered as synapses definition**



---


### Life Example ###
```
[SYNAPSES]
ampa={	'module': 'h.Exp2Syn',
	'tau1':0.1, 'tau2':0.8, 'e':0.0
	}
glyc={	'module': 'h.Exp2Syn',
	'tau1':0.1, 'tau2':1.2, 'e':-70.0
	}
```

|[POPULATIONS section <PREVIOUS](POPULATIONS.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT> CONNECTIONS section](CONNECTIONS.md)|
|:----------------------------------------------|:----------------------------------------------------------|:------------------------------------------|
