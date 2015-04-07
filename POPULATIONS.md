# POPULATIONS Section #
**Warning!** In POPULATION section arbitrary options are not allowed. **Each option in POPULATION Section is considered as population definition**
Each population option is a list of of three and more items.
  * First item is a range of cluster nodes where this cell type should be hosted. It may be:
    * _integer number_ - all cells should be hosted at node with particular rank (ID);
    * _None_ - all cells should be hosted at all available nodes
    * _list_ - is a list of node there these cells should be hosted.
  * Second item is an integer. It defines number of cells in population
  * Third and all other items are definition of cells within the population.

Each definition of cells is a _list_ of 5 items:
|1|_sting_| | name of Python objects which represents this cell type (see [CELLS section](CELLS.md)) |
|:|:------|:|:---------------------------------------------------------------------------------------|
|2 |_int_|  | number of global ID which will be assigned for each object. Please take into account that one Python object can be more than one sources of spikes, so it needs more than one global ID. See [NEURON parallel mechanisms](http://www.neuron.yale.edu/neuron/static/papers/jnm/parallelizing_models_jnm2008.pdf) for better understanding of global ID concept.|
|3 |_list of Python objects_ or _string_|  | Marker for each cell in the population. If it is a _string_, all cell would be marked by this string. If it is a _list_ the number of items in the list should be equal to a number of global ID in each cell object|
|4 |_dictionary_| **(!)** |Parameters which are passed to cell object.|
|5 |_float_ or _function_ | **(!)** |probability that cell type will be included into population|

**(!)** - values in dictionary and probabilities may be a function from ONE variable. This function will be called by script for each cell object. The variable passed to function changes from the zero to the one while index of cell goes from the beginning of population to the end. Please take into account that both zero and one are included into the reange of this variable.


### Tricks and Useful Technics ###
**>** Whole range of MPI hosts is held in `@GENERAL:NODERANGE@`. So if you would like to distribute some cell type only to even hosts you can use this notation `@GENERAL:NODERANGE@[2::2]`

**>** Multiple cell objects allow you create population which consists two and more distinguish cell types. For example, in some population there are two cell types, type-1 and type-2. Let for some sensory-topical organization at the beginning of population type-1 cells appears more off ten than type-2, and vice versa. Let total number of both types cell is 200. A population option should be defined as following:
```
pop=[None,['type-1',100,1,{},lambda x:1-x],['type-2',100,1,{},lambda x:x]]
```

**>** Functions in parameters _dictionary_ allow create gradient of ion channels cross the population. For example if h-channel more express in one side of the population and less in the other, a population option has to be defined as fallowing:
```
pop=[None,['some-cell',200,1,{ghbar=labmdax:0.5+x*0.5},1] ]
```
In this example maximal conductance of h-channel will 0.5 at the beginning of population and 1.0 at the end.

**>** Use same [units](http://www.neuron.yale.edu/neuron/static/docs/units/unitchart.html) as NEURON



---


### Life Example ###
```
left-input	= [  0, 1,
		[ 'AN',
			@AUDITORY NERVE:nhcell@ * @AUDITORY NERVE:nfibperhcell@,
			[ (f[0],t) for f in @AUDITORY NERVE:anconfig@[0] for t in f[1:] ],
			{
				'anconfig':@AUDITORY NERVE:anconfig@[0],
				'isright':False
			},
			1
		]
	]

right-input	= [  1, 1,
		[ 'AN', 
			@AUDITORY NERVE:nhcell@ * @AUDITORY NERVE:nfibperhcell@,
			[ (f[0],t) for f in @AUDITORY NERVE:anconfig@[1] for t in f[1:] ],
			{
				'anconfig':@AUDITORY NERVE:anconfig@[1],
				'isright':True
			},
			1
		]
	]

left-sbc = [@GENERAL:NODERANGE@[2:], 120,
		[ 'VCN', 1, 'TypeII',
			{
				'Type':'"Type II"'
			},
			lambda x: 1. - x,
		],
		[ 'VCN', 1, 'Type I-c',
			{
				'Type':'"Type I-c"'
			},
			lambda x: x,
		]
	]

right-gbc = [ @GENERAL:NODERANGE@[2:], 120,
		[ 'VCN', 1, 'Type I-c mod',
			{
				'Type':'"Type I-c"',
				'Param':{
					'vcnklt.gkltbar':lambda x: float(1.-x)*1.67e-2,
					'vcnih.ghbar'   :lambda x: float(1.-x)*(1.67e-3-4.2e-5)+4.2e-5
				}
			},
			1
		]
	]

left-lso = [ None, 120,
		[ 'LSO', 1, 'LSO cell',
			{},
			1
		]
	]

```

|[CELLS section <PREVIOUS](CELLS.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[[NEXT> SYNAPSES section](SYNAPSES.md)|
|:----------------------------------|:----------------------------------------------------------|:-------------------------------------|