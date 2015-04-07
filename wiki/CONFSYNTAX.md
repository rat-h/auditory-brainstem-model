# Syntax of Model Description File #

## Basics ##
In general all model parameters are split on _sections_ and _options_.
Each _section_ starts from _section name_ in square parentheses. For example:
```
[This is a SECTION]
```

Everything after the _section name_ is a _section body_ until new section is defined or end of file.

A _section_ may (but, may not) contain one or more _options_. Each _option_ start from _option name_ then singe equal '_=_' or column '_:_' and option value. Here an example:
```
#Here first section stats
[SECTION ONE]
x=1 # That is option x
y=2 # That is option y

#Here first section end and start second section
[SECTION SECOND]
a=2 # That are the options of second section
b=3 #
x=7 # Please note that option name mat be same for different sections
#the end of file and second section
```

Each line started from space or tab is considered as continue of previous option. In this example
```
[SECTION]
x=1,
  2,
  3
```
x is actually 1,2,3

## Option Types, Links and Strings substitution ##
All option values in model description file are converted to Python objects automatically. This idea was so successful that we branch an independent Python module to provide same functionality for other Python projects. Please see [Config+Python project ](https://code.google.com/p/confpluspy/) for more details.

### Integers, Floats, Strings, Lists, Tuples and Dictionaries ###

First of all standard Python types are converted to Python [objects](http://docs.python.org/2/library/stdtypes.html):
```
[TYPES]
int     = 5                 # This is integer
float 1 = 5.                # This is float
float 2 = 1e-4              #  and this is also float
list    = [ 1, 2, 3]        # This is a list.
tuple   = ( 3, 2, 4. )      # This is a tuple. 
dict    = {'a':1, 'b':2.3}  # This is a dictionary.
string  = 'This is a string'
#Long and complicated object can be spited on parts
long list = [
 'first list object is string'.
 2,                         # second list object is integer
 3.5                        # third list object is float
 ]                          # the end of long list
long dict = {
 'name':'sample',
 'age':'unknown',
 'duration':2.5
 } 
```

### Function and Inline computation ###

The usefulness of Python objects is in ability to define functions and make standard computations inline. For example
```
[FUNC]
func = lambda x: x**2 # func is a function
x    = 2.5 * 2        # x is equal to 5.
```

### Links Resolving ###
The next feature allows to use _value_ of previously defined _option_ in other _options_. For this, a _link_ block (or just _link_) should be included in a _option value_. Every _link_ has very simple syntax **@SECTION:OPTION@** which is commercial-at, name of section, column, name of option and commercial at again. Here an example how it works
```
[SEC-A]
x=2
y=3
[SEC-B]
sum = @SEC-A:x@ + @SEC-A:y@
```
In this example, after resolving to links @SEC-A:x@, @SEC-A:y@ and calculation with actual values, _sum_ is equal to 5, of course.

In same way it is possible to use functions in line:
```
[FUNC]
func = lambda x: x**2 
[COMP]
two squared = @FUNC:func@(2) # the _link_ is the function, so _link_(value) returns result of function form this value. 
```
In this example _two squared_ is equal to 4.... Simple!

### String Resolving ###
Finally it is useful to resolve _link_ into a string not Python objrct. This may be achieved by changing of commercial-at sign to dollar sign, i.e. **$SECTION:OPTION$**.
```
[VAR]
x=2
y=3
sum = @VAR:x@ + @VAR:y@ # here both links are resoled into Python objects, so computations are possible,
                        # i.e after resolving sum=2+3
str = $VAR:x$ + $VAR:y$ # in this case both links are resolved into strings, i.e. '2' and '3',
                        # so after resolving str='2'+'3', i.e. _string_ '23'
[PRINT OUT]
print="Sum of $VAR:x$ and $VAR:y$ is equal to $VAR:sum$"
                        # So now _links_ were resolved into _string_ objects: '2' '3' and '5' 
```
which create _print_ option with string _Sum of 2 and 3 is equal to 5_.

Please find more examples on [Config+Python website](https://code.google.com/p/confpluspy/)


---


Now we can consider main sections of a **Model Configuration File**

  * [GENERAL section](GENERAL.md)
  * [AUDITORY NERVE section](AUDNERVE.md)
  * [STIMULI section](STIMULI.md)
  * [CELLS section ](CELLS.md)
  * [POPULATIONS section](POPULATIONS.md)
  * [SYNAPSES section](SYNAPSES.md)
  * [CONNECTIONS section ](CONNECTIONS.md)
  * [RECORD section](RECORD.md)
  * [SIMULATION section](SIMULATION.md)
  * [GRAPHS section](GRAPHS.md)
  * [VIEW section](VIEW.md)
  * [STAT section](STAT.md)

|[How to Create and Simulate a Model< Previous](HOWTO.md)|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT> GENERAL section](GENERAL.md)|
|:-------------------------------------------------------|:----------------------------------------------------------|:----------------------------------|