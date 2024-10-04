# meltools
open tools for MELCOR on Linux 

## Contains
- `browseptf/browseptf.py` -- a python-based GUI to browse MELCOR PTF files
- `melbash` -- various simple bash scripts
    - `dogpl.sh` -- runs GnuPlot on all files with suffix `.gpl`
    - `lmelcor*.sh` -- prints all running MELCOR processes (either `melcor` or `melcor2`)
    - `lmelstp.sh` -- ???
    - `lmeltail.sh` -- ???
- `melendf` -- ???
    - uncompress the endf files from `data-endf.tar.xz` (they are compressed to avoid large amount of large text files in git)
- `meltoolspython` -- ???
- `readptf`
    - `readptf` -- executable to read MELCOR PTF files
    - `tranptf` -- ???

## Installation of readptf
1. clone this repository
2. `cd readptf`
3. `make`
4. One of the following
    - `sudo make install` -- copies executables to `/usr/local/bin`
    - `export PATH=$PATH:$(pwd)` -- adds `readptf` directory to `PATH`
