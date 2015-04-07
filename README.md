## Auditory Brainstem Project ##
**Auditory Brainstem Project** is a software framework for _[NEURON+Python](http://frontiersin.org/neuroinformatics/paper/10.3389/neuro.11/001.2009/)_ with MPI or threading [parallelization](http://www.neuron.yale.edu/neuron/static/papers/jnm/parallelizing_models_jnm2008.pdf). Ultimate goal of this project is provide a simple, flexible environment to create large-scale model, run simulations and analysis results of simulations for neural networks naturally split on distinctive nuclei. For more scientific details please visit  **[main project's webpage](http://sites.google.com/site/auditorybsmodel/)**

This code is designed to run through [NSG Portal](http://www.nsgportal.org/).
It allows separate single-tread code, like setting network connectivity up, generating stimuli, collecting and indexing data, statistic analysis and graphics plotting from parallel code, i.e. actual simulation. As a result one should launch the application at least twice, but in wast majority cases three times with different command line keys. First to build model, this stage is called '_preset_'. Then second time to run a simulation, this may be done on different computer and/or NSG portal. And finally the third time to index recordings, make statistic analysis and figures plotting.
Please find more details in [User guide page](wiki/HOWTO.md)

## Current Status of Project ##
Currently this project has **unstable/experimental** status and totally in the developing stage. We plan to create a stable branch and make first stable commit in a few months.

## How to get it? ##
The code is distributed under [GNU GPL v3 License](http://www.gnu.org/copyleft/gpl.html).

Although it may be downloaded as [zip](https://github.com/rat-h/auditory-brainstem-model/archive/master.zip) archive, it is better to clone latest version from repository. For MacOS or Linux operating system, you need to open the terminal and run git program:
```
https://github.com/rat-h/auditory-brainstem-model.git
```

## Requirements ##
The project requites _[NEURON+Python](http://neuron.yale.edu/neuron/)_ software to run a simulation and standard scientific package for Python which is
  * [NumPy](http://www.numpy.org/)
  * [SciPy](http://www.scipy.org/)
  * [MatPlotLib aka pyplot](http://matplotlib.org/)

The project was tested mostly under Ubuntu or openSUSE Linux and NSG portal. The project was successfully run on MacOS computer, but terminal skills are required.


## How to report a BUG? ##
The main advantage of open source project it is fast track of bug and bug fixing system. Please use [project bug report system](https://github.com/rat-h/auditory-brainstem-model/issues) to post any issue.

## Code Browsing ##
Anyone can browse the code, commits and branches using  [project web interface](https://github.com/rat-h/auditory-brainstem-model). Please feel free to make you comments on files and wiki pages.

## How to Contribute to project? ##
The simplest way to do this is became a [Git Hub](http://github.com) user and add yourself to project developers. An other way is use git as main platform. So make you changes in local repository and send me your patch  on ruben.tikidji.hamburyan **AT** gmail.com
Please read [Git everyday](https://www.kernel.org/pub/software/scm/git/docs/everyday.html) to get familiar with git terminology.

## Links and External Code ##
Please note that this project contains external code:
  1. Original C-code of Zilany, M. S. A. and Carney, L.H. auditory nerve model which is published on [authors website](http://www.urmc.rochester.edu/labs/Carney-Lab). Please refer to original paper for proper citation:**Zilany, M. S. A. and Carney, L.H. (2010), Power-Law Dynamics in an Auditory-Nerve Model Can Account for Neural Adaptation to Sound-Level Statistics. (Journal of Neuroscience 30(31):10380-10390)**. <a href='Hidden comment: This code was included in project with authors permission.'></a>
  1. [GNU libresample](http://www-ccrma.stanford.edu/~jos/resample/) version 1.7 which is distributed under LGPL licence.
