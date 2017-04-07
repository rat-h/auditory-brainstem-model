# How to Create and Simulate a Model #

## Introduction ##
This **USER GUIDE** will help you to understand the concept of this project and finally give you step-by-step instructions how to create, run model and analyse results, using this project.

## Model description file ##
The model are totally defined in **model description file**, which has standard configuration format with Python expansion. The basic [syntax of model description file](CONFSYNTAX.md) allows you define set on stimuli for model activation, population of neurons, connections between populations, simulation parameters and results analyze.

## Main stages of modeling process ##
There are three stages of each simulation which are
  * **Preprocessing** aka preset
  * **Simulation**
  * **Indexing and Analyze** aka postset

![https://docs.google.com/drawings/d/1-_XKar5ANO_rBl_FvZ0PmoSMu_V7xwL-VFFURoCHMuM/pub?w=905&h=137&something.png](https://docs.google.com/drawings/d/1-_XKar5ANO_rBl_FvZ0PmoSMu_V7xwL-VFFURoCHMuM/pub?w=905&h=137&something.png)

Let look at each stage separately.

### Preprocessing (preset) ###
Fro preprocessing script may be run both under Python or NEURON environment. To lunch script with python you should run following command to prepare the model to [Run Locally](LOCAL.md)
```
$python (path to mainmodel.py) --no-run
```
or fallowing command to prepare model to [Run through NSG portal](NSG.md)
```
$python (path to mainmodel.py) --preset-only
```
Same commands with NEURON environment:
```
$nrngui -nogui -python -isatty (path to mainmodel.py) --no-run 
# OR to prepare for NSG portal:
$nrngui -nogui -python -isatty (path to mainmodel.py) --preset-only
```

In this stage:
  1. The script creates stimuli to activate model based on [STIMULI section](STIMULI.md) of **[model description file](CONFSYNTAX.md)**. The project uses Python wrapper for Zilany, M. S. A. and Carney, L.H. 2010 auditory nerve model to generate spike trains of auditory nerve fibers. The result files for each stimulus has [simple format](ANRESPGET#Stimulus_Format.md) which may be read by check-pkl script;
  1. Then it reads [POPULATIONS](POPULATIONS.md), [SYNAPSES](SYNAPSES.md), [CONNECTIONS](CONNECTIONS.md) and [RECORD](RECORD.md) sections and creates network file. The name of network file is defined by _networkfilename_ option in [GENERAL](GENERAL.md) section of **[model description file](CONFSYNTAX.md)**.
  1. Finally, it copies NEURON _mod_ files into root directory and if it runs [Locally](LOCAL.md) call _nrnivmodl_ (or any other compiler which may be defined by `--mod-compiler=` [command line key](BUILD_and_RUN.md)) to compile them.

### Simulation ###
In this stage script should be run **ONLY** under NEURON environment.
```
$[mpyrun -hosts=... -n=...] nrngui -nogui -python -isatty [-mpi] (path to mainmodel.py)
```

The NEURON may be run in parallel environment, i.e. MPI, and each thread or each MPI instance performs next actions:
  1. Reads network file and creates cell which should be hosted at this particular node.
  1. Creates synapses and connects these synapses to the source with global ID
  1. Sets up recorders
  1. **> Loads stimulus and activates input elements**
  1. **> Runs the simulation**
  1. **> Saves result of simulation into a file**
  1. Repeats steps 4, 5 and 6 for all stimuli

### Analyze ###
This stage may be done under both Python and NEURON environment.
To get a graphs and statistic launch the script with three extra keys.
```
$python (path to mainmodel.py) --no-run --graphs --stat
```

In this stage:
  1. The script collects and indexes all files for all stimuli. It may be process separately if script is lunched with '--no-run --collect' [command line keys](BUILD_and_RUN.md) only.
  1. If it is launched with '--graphs' key, it reads [GRAPHS section](GRAPHS.md) and shows graphs in screen or/and save into a file(s).
  1. If it is launched with '--stat' key, it reads [STAT](STAT.md) section and prints the results of statistic analyses to the standard output console as well as to csv file

### Stages and key diagrame ###
![https://docs.google.com/drawings/d/1W17nY6YlJItn5Oo_SE2gv_o09bpHl1LQin-GIzlWC_o/pub?w=824&h=753](https://docs.google.com/drawings/d/1W17nY6YlJItn5Oo_SE2gv_o09bpHl1LQin-GIzlWC_o/pub?w=824&h=753)

| < Previous|[Home](https://code.google.com/p/auditory-brainstem-model/)|[NEXT> Model configuration file](CONFSYNTAX.md)|
|:----------|:----------------------------------------------------------|:----------------------------------------------|
