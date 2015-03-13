# Command line Keys #

_mainmodel.py_ has several command line keys which defined it behavior. You can print out all keys with short description, if you launch _mainmodel.py_ with '--h' key. This is only one key which you need to remember, all others willbe printed out on your screen.
```
$python mainmodel.py -h

USAGE: python|nrngui -nogui -python|mpirun -hosts... -h nrngui -nogui -python -mpi|something_else mainmodel.py [OPTIONS]
OPTIONS:
   -h|-help|--h|--help            : prints this help and exit
   --config=configuration_file    : sets configuration file [default: mainmodel.cfg]
   --log=log_file                 : sets log file [default: mainmodel.log for local run and log/node#.log for MPI run]
   --log-level=DEBUG|INGO|WARNING|ERROR|CRITICAL|
                                  : sets log level [default: DEBUG or INFO]
   --no-run                       : prevents the simulation. This option allows analysis results of simulation without
                                    re-simulation. You can make an rsults analysing in the Python whithout NEURON:
                                     python mainmodel.py --no-run --graphs
   --mod-compiler=compiler_prog   : set compiler program for NEURON mod files [default: nenivmodl]
   --preset-only                  : makes preset(preprocessing) procedures and exit
                                    preset totally sets network (generates networkfile), copies all modules to root
                                    directory and calculate 'fingerprint' of model. After preset configuration file
                                    can NOT be modified! Use --preset-only option to prepare the job for NSG portal
   --non-parallel                 : prevents parallel running
   --non-threads                  : prevents using multithreading
   --collect                      : makes and index of all recorded cells and writes an index and all recordings in one file
                                    if you run --graphs or other post-processing procedures, collection will be made
                                    automatically
   --graphs                       : reads GRAPHS section of configuration file or alternative configuration file 
                                    (see --config-exp) to draw or/and show results of simulations
   --config-exp=another_configuration_file
                                  : expands configuration file and alters all post-processing options.
                                    Use this option for multiple analyses of simulation results. This option does not alter
                                    main configuration file and model fingerprint (so do not trigger simulation) in preset
                                    and simulation stages but reset sections [GRAPHS], [VIEW] and so on in post-processing.
                                    This expands all sections in the main configuration, so be careful with section/option
                                    duplication, this will raise and error

```