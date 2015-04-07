# STIMULI section of Model Description File #

Stimuli section has only one required options
| **Option** | **Option type** | **Description** |
|:-----------|:----------------|:----------------|
|stimuli| _string_  or _list_ of _strings_ |  Each _string_ is considered as options in STIMULI section with stimulus parameters.|

### Stimulus Definition ###
Each stimulus option is a list for 4 objects.
|**#**|**Type**| **Description** |
|:----|:-------|:----------------|
| 1 | _string_ | Name of stimulus file |
| 2 | _dictionary_ | Dictionary of parameters and values of stimulus. Only one parameter _stimtype_ is obligatory. Please find full [list of paramters and default values](ANGEN.md) |
| 3 | _tuple_ of length 2 or set of _tupels_ of length 2; each item in tuple is _string_ | set of pear _population name_ and _function name_. For each cell in population with specified _population name_ (see [POPULATIONS section](POPULATIONS.md)), function with _function name_ will call to read particular stimulus file. Name of stimulus file is passed as first parameter of this function. |
| 4 | _string_ | Name of out put file |

### Tricks and Useful Technics ###
  * Input/Output directories. We anchorage you create and actively use additional option, such as separate directory for stimulus files and output files. Example `Datadir = '$GENERAL:working dir$/Dataset$'`. You can use $STIMULI:Deatadir$ resolving to define stimulus names (first item in stimulus definition).
  * Use unique name body. For each stimulus file you should provide unique name. However it is useful to have some common part in names to indicate same set of simulations. You can create name-body option and use it in both names of input and output files.
  * Another approach to make unique file names is in using model 'fingerprint' in name. Model fingerprint is available as $GENERAL:CONFIGHASH$ string.



---


### Life Example ###
```
[STIMULI]
stimdir		= @GENERAL:working dir@+'/Dataset/'
outputdir	= @GENERAL:working dir@+'/Results/'
prog		= @GENERAL:prefix@+'/an-response-generator'
stimuli		= ['click-itd-100us','click-itd-000us','click-itd+100us']
namebody	= '-20hc-fr58_62kHz_unif-20fphc'

click-itd-100us = [
	@STIMULI:stimdir@+'/click-itd-100us'+@STIMULI:namebody@+'.spkl',
	{
		'stimtype'			: 'click',
		'interaural time difference'	: -0.1e-3,
	},
	(('left-input','readfile'),('right-input','readfile')),
	@STIMULI:outputdir@+'/click-itd-100us'+@STIMULI:namebody@+'.pkl'
	]

click-itd-000us = [
	'$STIMULI:stimdir$/click-itd-000us$STIMULI:namebody$.spkl',
	{
		'stimtype'			:'click',
		'interaural time difference'	: 0.0,
	},
	(('left-input','readfile'),('right-input','readfile')),
	'$STIMULI:outputdir$/click-itd-000us$STIMULI:namebody$.pkl'
	]
click-itd+100us = [
	'$STIMULI:stimdir$/click-itd+100us$STIMULI:namebody$.spkl',
	{
		'stimtype'			: 'click',
		'interaural time difference' 	: 0.1e-3,
	},
	(('left-input','readfile'),('right-input','readfile')),
	'$STIMULI:outputdir$/click-itd+100us$STIMULI:namebody$.pkl'
	]

```

|[AUDITORY NERVE <PREVIOUS](AUDNERVE.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[[NEXT> CELLS section](CELLS.md)|
|:--------------------------------------|:----------------------------------------------------------|:-------------------------------|