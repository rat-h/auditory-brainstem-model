# CONNECTIONS section #
**Warning!** In CONNECTIONS section arbitrary options are not allowed. **Each option in CONNECTIONS Section is considered as connection definition**



---


### Life Example ###

```
[CONNECTIONS]
left-input2left-sbc=['left-input','left-sbc',
	True, False,
	lambda x: np.random.randint(2,high=5),
	lambda x,y: bool( np.random.rand() < np.exp(-(x-y)**2/0.4**2) ),
	3e-3,
	lambda x,y: np.abs(x-y)*0.5+0.1,
	('soma',0.5),
	'ampa'
	]

right-input2right-gbc=['right-input','right-gbc',
	False,False, 
	lambda x: np.random.randint(10,high=50),
	lambda x,y: bool( np.random.rand() < np.exp(-(x-y)**2/0.2**2) ),
	5e-3,
	lambda x,y: np.abs(x-y)*0.5+0.1,
	('soma',0.5),
	'ampa'
	]
left-sbc2left-lso=['left-sbc','left-lso',
	True,False,
	lambda x: np.random.randint(5,high=11),
	lambda x,y: bool( np.random.rand() < np.exp(-(x-y)**2/0.4**2) ),
	6e-3,
	lambda x,y: np.abs(x-y)*0.5+0.1,
	([ 'dends[0]', 'dends[1]'][np.random.randint(2)],lambda x,y:float(np.random.randint(10))/10.),
	'ampa'
	]
right-gbc2left-lso=['right-gbc','left-lso',
	True,False,
	lambda x: np.random.randint(1,high=4),
	lambda x,y: bool( np.random.rand() < np.exp(-(x-y)**2/0.4**2) ),
	1e-3,
	lambda x,y: np.abs(x-y)*0.5+0.1,
	('soma',0.5),
	'glyc'
	]
```


|[SYNAPSES section <PREVIOUS](SYNAPSES.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT>RECORD section](RECORD.md)|
|:----------------------------------------|:----------------------------------------------------------|:-------------------------------|