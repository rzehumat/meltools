#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 python script cvh-liqlev.py 
 written by Petr Vokac, UJV Rez, a.s.
 December 2008, 
 August 2009, 
 July 2010,
 March 2011 - use of pvpyx
 August 2017 -- change of modules structure
 License: as-is

 expects "readptf.exe" on PATH !

expects cvh-liql config name as command 
line argument (on default provided)

specific input options:

scvhlist    file name of cvh list for cvh-* plots

scvhlist should be formated :

cvxxx x0 vsc

where: 

xxx is the volume number
x0  is the volume offset on the x axis
vsc is the volume scale factor

see function pvpyx.fGetCVROffset for details

'''

import meltoolsmod.cvhliqlev as cvhliqlev
if __name__ == "__main__":
 cvhliqlev.fMain()
pass    
