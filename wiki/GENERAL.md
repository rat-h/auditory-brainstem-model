# GENERAL section of Model Description File #

General section contains several required options

| **Option** | **Option Type** | **Description** |
|:-----------|:----------------|:----------------|
|networkfilename|_string_|Name of network file|
|pyextrapath|_string_ or _list of strings_|Paths which should be add to Python sys.paths variable to allow Python to find a modules. It may be empty (actually not good idea to keep ti empty. If you thing it should be empty, some thing wrong with your model!) |

### Tricks and arbitrary options ###
As you can understand from [basics of model description file](CONFSYNTAX.md) one can add arbitrary number of extra options to section. **It is not true for several sections of model description file**, but it is true for _GENERAL_ section. We strongly recommend to add options like 'prefix' or 'source' to your _GENERAL_ section. In simplest way you can set it to empty string or to './' . The second step of this trick is add link to 'pyextrapath' option and to many other options along your model description file. It looks like this:
```
[GENERAL]
prefix			= './'
pyextrapath		= ('$GENERAL:prefix$/lib','$GENERAL:prefix$/cells')
```

Now you would like to make some small experiment with your model aside of main directory. So you create new directory and copy there your file.
```
$mkdir ../small-test && cp maymodel.cfg ../small-test/test.cfg && cd ../small-test
```

If you defined your paths explicitly (without _prefix_ or _source_ options), you would need to correct all paths along the file. However if you use relative paths (with _prefix_ or _source_ option) you need adjust only prefix option, and that's it! For example in file test.cfg in small-test directory you need just reset prefix like this:
```
[GENERAL]
#previously prefix was set on current directory, i.e. './'
#but now we need to reset it to directory with modules
prefix			= '../auditory-brainstem-model/'
pyextrapath		= ('$GENERAL:prefix$/lib','$GENERAL:prefix$/cells')
```
Now _pyextrapath_ is pointed on to directories '../auditory-brainstem-model/lib' and '../auditory-brainstem-model/cells', which are absolutely correct paths.


---


### Life example ###
```
[GENERAL]
prefix			= '../'
working dir		= './'
pyextrapath		= ('$GENERAL:prefix$/lib','$GENERAL:prefix$/cells')
networkfilename		= @GENERAL:working dir@+'/network.pkl'
```


|[Model configuration file <PREVIOUS](CONFSYNTAX.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT > AUDITORY NERVE](AUDNERVE.md)|
|:--------------------------------------------------|:----------------------------------------------------------|:-----------------------------------|