#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

python script cor-volf.py 
written by Petr Vokac, UJV Rez, a.s.
December 2008, August 2009, June 2010, March 2011
August 2017 -- change of modules structure
License: as-is

depends on:
PyX http://pyx.sourceforge.net/ http://pypi.python.org/pypi/PyX/
 (and PyX depends on TeXLive)
PDFtk  http://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/

expects "readptf.exe" on PATH !

expects cor-volf.conf configuration file in the current folder
other configuration file can be specified as the first command line
argument

components specified in the sCompList are plotted in the order
as found in the list

debris bed porosity should not be requested for plot,
it is added to debris bed automatically

scCompList should contain the same number of items as
sCompList

25.9.2014: handling of noutfdig

25.8.2017: pvmisc and pvpyx modules moved to meltoolsmod
           the main code moved to module corvolf.py

"""

import meltoolsmod.corvolf as corvolf

if __name__ == "__main__":
    corvolf.fMain()
pass
